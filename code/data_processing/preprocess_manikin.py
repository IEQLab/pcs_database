import os
import logging
import numpy as np
import pandas as pd
import chardet
import re
from collections import defaultdict
from dataclasses import asdict
import data_processing.database_columns_names
import utils.utilities
from data_processing import calc_equivalent_temperature
from data_processing import preprocess_chamber
from config.configuration import Config


# TODO: Add chamber info to this dataset
# TODO: Think the way to organize the impact of PCS - maybe hc or v for fans and Teq for heaters
# Step 1: Detect file encoding
def detect_encoding(file_path):
    """
    Detect the file encoding using chardet.
    """
    with open(file_path, "rb") as file:
        raw_data = file.read()
        return chardet.detect(raw_data)["encoding"]


# Step 2: Load CSV file
def load_data_with_custom_columns(file_path, custom_columns, strict_datetime=True):
    """
    Load a CSV file, assign custom column names, and set the datetime index.
    Allows for flexible fallback parsing of datetime when strict parsing fails.

    Args:
        file_path (str): Path to the CSV file.
        custom_columns (list): Custom column names to apply.
        strict_datetime (bool): If True, use strict format; if False, use auto-detection.
    Returns:
        pd.DataFrame: A cleaned DataFrame with proper column names and datetime index.
    """
    # Detect encoding to ensure correct loading
    encoding = detect_encoding(file_path)

    # Read CSV, skipping the first 5 rows (likely metadata or notes)
    df = pd.read_csv(file_path, encoding=encoding, skiprows=5, header=None)

    # Drop the last column if it is completely empty (artifact from Excel-like tools)
    if df.iloc[:, -1].isnull().all():
        df = df.iloc[:, :-1]

    # Assign consistent column names
    df.columns = custom_columns

    # Try parsing the 'Datetime' column
    if strict_datetime:
        # Use strict parsing for speed and consistency (format must match exactly)
        df["Datetime"] = pd.to_datetime(
            df["Datetime"], format="%d/%m/%Y %I:%M:%S %p", errors="coerce"
        )
    else:
        # Fallback: let pandas guess the format (slower but handles inconsistent formats)
        df["Datetime"] = pd.to_datetime(df["Datetime"], errors="coerce")

    # Use Datetime as the DataFrame index
    df.set_index("Datetime", inplace=True)

    # Replace any empty string cells with proper NaN
    df.replace(r"^\s*$", np.nan, regex=True, inplace=True)

    return df


# Step 3: Calculate averages for the last minute of data
def average_last_five_minute(file_path, custom_columns):
    """
    Calculate averages for the last five minutes of data.
    [IMPORTANT!!!} If strict datetime format fails, fallback to flexible parsing to avoid skipping files.
    For some reason the datetime format in the manikin's csv files are different, the code try to read fast but not having too much warming!
    """
    try:
        # Step 1: Try loading data using a strict datetime format (fast and predictable)
        df = load_data_with_custom_columns(
            file_path, custom_columns, strict_datetime=True
        )

        # Step 2: If the result is empty or all datetimes failed to parse, try again without format
        if df.empty or df.index.isna().all():
            # This fallback uses automatic datetime parsing (more tolerant but slower)
            df = load_data_with_custom_columns(
                file_path, custom_columns, strict_datetime=False
            )

        # Step 3: Calculate averages over the last 5 minutes of available data
        last_five_minute_start = df.index.max() - pd.Timedelta(minutes=5)
        last_five_minute_data = df[df.index > last_five_minute_start]

        if not last_five_minute_data.empty:
            # Step 4: Compute column-wise mean and add metadata
            averages = last_five_minute_data.mean(numeric_only=True).to_frame().T
            averages["Reference_time"] = last_five_minute_data.index.mean().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            averages["File_name"] = os.path.basename(file_path)
            return averages

    except Exception as e:
        # Log and skip any file that causes unexpected errors
        print(f"[SKIPPED] {file_path} - Error: {e}")

    return None


# Step 4: Search for files by keyword
def find_files_with_keyword(folder_path, keyword, exclude_folders=["Old", "UFAD"]):
    """
    Search for files in a folder containing a specific keyword in their names,
    while avoiding files inside specific folders.

    Parameters:
        folder_path (str): The path to the root folder to search.
        keyword (str): The keyword to search for in file names.
        exclude_folders (list): A list of folder names to exclude.

    Returns:
        list: A list of file paths matching the criteria.
    """

    result_files = []

    for root, _, files in os.walk(folder_path):
        # Skip directories that are in the exclude list
        if any(excluded in root.split(os.sep) for excluded in exclude_folders):
            continue

        # Add files that contain the keyword in their names
        result_files.extend(
            os.path.join(root, file) for file in files if keyword in file
        )

    return result_files


def extract_info_from_filename(filename):
    filename = os.path.basename(filename).split(".")[0]
    parts = filename.split("_")

    dict_extracted_info = {
        "PCS_ID": None,
        "PCS_Name": None,
        "PCS_Level": None,
        "Angle_Horizontal": None,
        "Distance_Horizontal": None,
        "Ta": None,
        "Control_Method": None,
    }

    try:
        # ID: Extract with regex
        match = re.search(r"ID(\d+)", filename)
        if match:
            dict_extracted_info["PCS_ID"] = int(match.group(1))
        else:
            logging.warning(
                f"[extract_info_from_filename] No valid ID found in: {filename}"
            )

        # PCS_name and Level (parts[2], parts[3]) with safety check
        dict_extracted_info["PCS_Name"] = parts[2] if len(parts) > 2 else None
        dict_extracted_info["PCS_Level"] = parts[3] if len(parts) > 3 else None

        for part in parts[4:]:
            if part.startswith("Angle"):
                dict_extracted_info["Angle_Horizontal"] = int(part.replace("Angle", ""))
            elif part.startswith("Distance"):
                dict_extracted_info["Distance_Horizontal"] = int(
                    part.replace("Distance", "")
                )
            elif part.startswith("Ta"):
                dict_extracted_info["Ta"] = int(part.replace("Ta", ""))
            elif "Control" in part:
                dict_extracted_info["Control_Method"] = part

    except Exception as e:
        logging.error(f"[extract_info_from_filename] Failed to parse: {filename} ({e})")

    return dict_extracted_info


def match_nearest_datetime(df_manikin, df_chamber):
    # Ensure a copy is made to avoid SettingWithCopyWarning
    df_manikin = df_manikin.copy()

    # Convert date columns to datetime format
    df_manikin.loc[:, "Reference_time"] = pd.to_datetime(
        df_manikin["Reference_time"], errors="coerce"
    )

    # Ensure df_chamber's index is DatetimeIndex
    df_chamber.index = pd.to_datetime(df_chamber.index, errors="coerce")

    # Drop NaT values to prevent errors
    df_manikin = (
        df_manikin.dropna(subset=["Reference_time"])
        .sort_values("Reference_time")
        .reset_index(drop=True)
    )
    df_chamber = df_chamber.dropna().sort_index()  # Sort by index

    # Function to find the nearest Datetime
    def find_nearest(row, df_chamber):
        if pd.isna(row["Reference_time"]):
            return pd.Series(
                dtype="object"
            )  # Return an empty row if Reference_time is NaT

        reference_time = pd.to_datetime(
            row["Reference_time"], errors="coerce"
        )  # Ensure datetime format

        # Check if reference_time is within the range of df_chamber.index
        if (
            reference_time < df_chamber.index.min()
            or reference_time > df_chamber.index.max()
        ):
            logging.info(
                f"Reference Time {reference_time} is out of range ({df_chamber.index.min()} - {df_chamber.index.max()})"
            )
            return pd.Series(dtype="object")  # Return an empty row if out of range

        # Compute time differences (Convert Index to Series)
        timedelta_values = pd.Series(
            (df_chamber.index - reference_time) / pd.Timedelta(seconds=1),
            index=df_chamber.index,
        )

        # Find nearest index using idxmin()
        nearest_idx = timedelta_values.abs().idxmin()

        logging.info(f"Reference Time: {reference_time}")
        logging.info(f"Nearest Index: {nearest_idx}")
        logging.info(
            f"Timedelta Difference: {timedelta_values.loc[nearest_idx]}"
        )  # Debugging

        # Check if nearest time is within ±1 minute (60 seconds)
        min_difference = timedelta_values.abs().min()
        if min_difference > 60:
            logging.info(
                f"Warning: Nearest available data for {reference_time} is {min_difference:.1f} seconds away at {nearest_idx}."
            )

        return df_chamber.loc[nearest_idx]

    # Apply function to find nearest datetime
    matched_data = df_manikin.apply(lambda row: find_nearest(row, df_chamber), axis=1)

    # Merge the matched data
    df_matched = pd.concat(
        [df_manikin.reset_index(drop=True), matched_data.reset_index()], axis=1
    )

    return df_matched


# Apply `extract_info_from_filename` function to add extracted information to `delta_results`
def add_extracted_info_to_dataframe(df):
    """
    Adds extracted file information (ID, PCS_name, Level, etc.) to the delta_results DataFrame,
    placing the extracted columns at the beginning (excluding the index).

    Args:
        df (pd.DataFrame): DataFrame containing 'Condition_with_PCS' and 'Condition_without_PCS' file names.

    Returns:
        pd.DataFrame: Updated DataFrame with extracted columns placed at the leftmost side.
    """
    extracted_data = []

    for _, row in df.iterrows():
        # Extract information from the PCS file name
        with_pcs_info = extract_info_from_filename(row["Condition_with_PCS"])
        print(with_pcs_info)

        # Store extracted data along with original row, placing extracted info first
        extracted_data.append(
            {
                **row.to_dict(),  # Add original delta values first
                "PCS_ID": with_pcs_info["PCS_ID"],
                "PCS_Name": with_pcs_info["PCS_Name"],
                "PCS_Level": with_pcs_info["PCS_Level"],
                "Angle_Horizontal": with_pcs_info["Angle_Horizontal"],
                "Distance_Horizontal": with_pcs_info["Distance_Horizontal"],
                "Tset": with_pcs_info["Ta"],
                "Control_Method": with_pcs_info["Control_Method"],
            }
        )

    # Convert list of dictionaries to DataFrame
    updated_df = pd.DataFrame(extracted_data)

    # Reorder columns to ensure extracted info is at the left
    extracted_columns = [
        "PCS_ID",
        "PCS_Name",
        "PCS_Level",
        "Angle_Horizontal",
        "Distance_Horizontal",
        "Tset",
        "Control_Method",
    ]
    remaining_columns = [
        col for col in updated_df.columns if col not in extracted_columns
    ]

    # Reorder DataFrame
    updated_df = updated_df[extracted_columns + remaining_columns]

    return updated_df


def drop_group_a_b_columns(df):
    cols_to_drop = [
        col for col in df.columns if ("Group A" in col) or ("Group B" in col)
    ]
    if cols_to_drop:
        logging.info(
            f"Dropping columns containing 'Group A' or 'Group B': {cols_to_drop}"
        )
    return df.drop(columns=cols_to_drop)


def generate_condition_pairs(matching_files):
    """
    Generate condition pairs for comparison based on date.

    Args:
        matching_files (list): List of file paths.

    Returns:
        list: List of tuples representing condition pairs.
    """
    # Dictionary to group files by date
    file_dict = defaultdict(list)

    for file_path in matching_files:
        # Extract file name from full path
        file_name = file_path.split("\\")[-1]  # For Windows, use `\` as the delimiter

        # Extract date in YYYY-MM-DD format
        match = re.search(r"(\d{4}-\d{2}-\d{2})", file_name)
        if match:
            date = match.group(1)
            file_dict[date].append(file_name)

    condition_pairs = []

    # Iterate through each date group
    for date, files in file_dict.items():
        # Extract NoPCS (ID0) files as without_PCS
        without_pcs = [f for f in files if "ID0_NoPCS" in f]
        # Extract other files as with_PCS
        with_pcs = [f for f in files if "ID0_NoPCS" not in f]

        # Create condition pairs: One NoPCS file paired with each PCS file
        if without_pcs:
            base_condition = without_pcs[0]  # Get the file name
            for pcs_file in with_pcs:
                pcs_condition = pcs_file  # Get the file name
                condition_pairs.append((base_condition, pcs_condition))

    return condition_pairs


# Step 5: Reorder columns based on the BodyPart dataclass
def reorder_columns(df):
    """
    Reorder the columns of a DataFrame based on the BodyPart dataclass.
    Ensures that 'Reference_time' is preserved.
    """
    # Generate ordered list of columns based on body parts
    new_columns_list = data_processing.database_columns_names.generate_columns(
        body_parts=utils.utilities.BodyPart
    )

    logging.info(f"new_columns_list: {new_columns_list}")

    ordered_columns = [col for col in new_columns_list if col in df.columns]
    remaining_columns = [col for col in df.columns if col not in ordered_columns]

    return df[ordered_columns + remaining_columns]


# Step 6: Calculate delta between conditions
def calculate_deltas(df, condition_pairs):
    """
    Compute the difference (delta) between condition pairs while preserving Reference_time.
    Includes PCS and Baseline values for P_, Tsk, Ta, RH, and ET.
    """

    results = []

    if "File_name" not in df.columns:
        if df.index.name == "File_name":
            df = df.reset_index()
        else:
            raise KeyError("'File_name' is missing from both columns and index!")

    # Identify relevant columns
    p_columns = [
        col
        for col in df.columns
        if col.startswith("P_") and not any(x in col for x in ["Group A", "Group B"])
    ]
    tsk_columns = [col for col in df.columns if col.startswith("Tsk_")]
    env_columns = ["Ta", "MRT", "RH", "V", "To", "ET"]

    for base_fname, pcs_fname in condition_pairs:
        base_row = df[df["File_name"].str.contains(base_fname, na=False, regex=False)]
        pcs_row = df[df["File_name"].str.contains(pcs_fname, na=False, regex=False)]

        if base_row.empty or pcs_row.empty:
            print(f"Skipped: base='{base_fname}', pcs='{pcs_fname}'")
            continue

        base_row = base_row.iloc[0]
        pcs_row = pcs_row.iloc[0]

        delta_row = {
            "Reference_time": pcs_row["Reference_time"],
            "Condition_without_PCS": base_fname,
            "Condition_with_PCS": pcs_fname,
        }

        # Add Delta values first
        for col in p_columns:
            delta_row[f"Delta_{col}"] = pcs_row[col] - base_row[col]

        # Then PCS values (first env, then Tsk, then P_)
        for col in env_columns + tsk_columns + p_columns:
            delta_row[f"PCS_{col}"] = pcs_row.get(col, np.nan)

        # Then Baseline values (same order)
        for col in env_columns + tsk_columns + p_columns:
            delta_row[f"Baseline_{col}"] = base_row.get(col, np.nan)

        results.append(delta_row)

    return pd.DataFrame(results)


def apply_htc_and_teq_calculation(
    df: pd.DataFrame,
    body_parts=None,
    q_prefix_pcs="PCS_P_",
    t_prefix_pcs="PCS_Tsk_",
    to_col_pcs="PCS_To",
    q_prefix_base="Baseline_P_",
    t_prefix_base="Baseline_Tsk_",
    to_col_base="Baseline_To",
) -> pd.DataFrame:
    """
    Calculate htc and Teq for PCS and Baseline, and their differences.
    Adds: PCS_ht_{part}, Baseline_ht_{part}, Delta_ht_{part},
          PCS_Teq_{part}, Baseline_Teq_{part}, Delta_Teq_{part}
    """

    # If no specific body parts are provided, use the default body part list
    if body_parts is None:
        body_parts = list(asdict(utils.utilities.BodyPart()).values())

    # Dictionary to temporarily store all new columns
    # This avoids WARNING to repeatedly modify the DataFrame during the loop,
    # which can lead to memory fragmentation and performance degradation.
    new_cols = {}

    for part in body_parts:
        q_pcs = f"{q_prefix_pcs}{part}"
        tsk_pcs = f"{t_prefix_pcs}{part}"
        q_base = f"{q_prefix_base}{part}"
        tsk_base = f"{t_prefix_base}{part}"

        pcs_ht = f"PCS_ht_{part}"
        base_ht = f"Baseline_ht_{part}"
        delta_ht = f"Delta_ht_{part}"
        pcs_teq = f"PCS_Teq_{part}"
        base_teq = f"Baseline_Teq_{part}"
        delta_teq = f"Delta_Teq_{part}"

        # Compute total heat transfer coefficient (htc) for PCS and Baseline
        new_cols[pcs_ht] = df.apply(
            lambda row: calc_equivalent_temperature.calculate_total_heat_transfer_coefficient(
                q_skin=row[q_pcs], t_skin=row[tsk_pcs], t_o=row[to_col_pcs]
            ),
            axis=1,
        )
        new_cols[base_ht] = df.apply(
            lambda row: calc_equivalent_temperature.calculate_total_heat_transfer_coefficient(
                q_skin=row[q_base], t_skin=row[tsk_base], t_o=row[to_col_base]
            ),
            axis=1,
        )
        new_cols[delta_ht] = new_cols[pcs_ht] - new_cols[base_ht]

        # Calculate Teq using pre-computed HTC values
        new_cols[pcs_teq] = df.apply(
            lambda row: (
                row[tsk_pcs] - row[q_pcs] / new_cols[pcs_ht][row.name]
                if new_cols[pcs_ht][row.name] != 0
                else np.nan
            ),
            axis=1,
        )
        new_cols[base_teq] = df.apply(
            lambda row: (
                row[tsk_base] - row[q_base] / new_cols[base_ht][row.name]
                if new_cols[base_ht][row.name] != 0
                else np.nan
            ),
            axis=1,
        )
        new_cols[delta_teq] = new_cols[pcs_teq] - new_cols[base_teq]

    df = pd.concat([df, pd.DataFrame(new_cols, index=df.index)], axis=1)

    return df.copy()


def reorder_final_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reorder final DataFrame columns in logical sequence:
    Reference info → environment → P/Tsk/ht/Teq (Delta → PCS → Baseline)
    """
    body_parts = list(asdict(utils.utilities.BodyPart()).values())

    # Step 1: Base information (always at the front)
    base_cols = ["Reference_time", "Condition_without_PCS", "Condition_with_PCS"]

    # Step 2: Environmental variables (include only if they exist in the DataFrame)
    env_cols = ["Ta", "RH", "MRT", "V", "To", "ET", "WBGT"]
    env_cols = [col for col in env_cols if col in df.columns]

    # Step 3: Physiological/heat-related variables in preferred order
    variable_groups = ["P_", "Tsk_", "ht_", "Teq_"]
    ordered_data_cols = []
    for var in variable_groups:
        for part in body_parts:
            for label in ["Delta", "PCS", "Baseline"]:
                col = f"{label}_{var}{part}"
                if col in df.columns:
                    ordered_data_cols.append(col)

    # Step 4: Collect any remaining columns not explicitly ordered
    known_cols = base_cols + env_cols + ordered_data_cols
    remaining = [col for col in df.columns if col not in known_cols]

    # Step 5: Return the DataFrame with columns reordered
    return df[base_cols + env_cols + ordered_data_cols + remaining]


# Main function
def main():
    """
    Main function to process all matching files and calculate averages.
    """
    try:
        # Load column format
        columns_format_file = os.path.join(
            Config.DataPaths.BASE_DIR, "columns_format.csv"
        )
        columns_format = pd.read_csv(columns_format_file).columns.tolist()

        df_chamber = preprocess_chamber.main()

        # print("df_chamber:", df_chamber)

        # Find all target files
        keyword = "TskControl"
        matching_files = find_files_with_keyword(
            folder_path=Config.DataPaths.RAW_DATA_DIR,
            keyword=keyword,
            exclude_folders=["Old", "UFAD"],
        )
        logging.info(f"matching_files: {matching_files}")
        if not matching_files:
            logging.info(f"No files found with the keyword {keyword}")
            return

        # Generate condition pairs based on date
        condition_pairs = generate_condition_pairs(matching_files=matching_files)
        logging.info(f"Generated condition pairs: {condition_pairs}")

        # Process each file
        all_averages = []
        for file_path in matching_files:
            logging.info(f"Processing file: {file_path}")
            averages = average_last_five_minute(
                file_path=file_path, custom_columns=columns_format
            )
            logging.info(averages)
            if averages is not None:
                averages = drop_group_a_b_columns(df=averages)
                all_averages.append(averages)
            else:
                logging.info(
                    f"No valid data found in the last minute for file: {file_path}"
                )

        # Combine and save results if there is data
        if all_averages:
            combined_averages = pd.concat(all_averages)
            logging.info(f"combined_averages: {combined_averages}")
            logging.info(f"columns of combined_averages: {combined_averages.columns}")

            # Reorder
            reordered_combined_averages = reorder_columns(df=combined_averages.copy())
            reordered_combined_averages = match_nearest_datetime(
                df_manikin=reordered_combined_averages, df_chamber=df_chamber
            )
            logging.info(f"reordered_combined_averages: {reordered_combined_averages}")
            logging.info(
                f"columns of reordered_combined_averages: {reordered_combined_averages.columns}"
            )

            # Summary of average data of each file
            file_name_to_save = os.path.join(
                Config.DataPaths.PROCESSED_DATA_DIR, "all_average_data.csv"
            )
            reordered_combined_averages.to_csv(file_name_to_save)
            logging.info(f"Saved averaged results of each file to {file_name_to_save}")
            logging.info(reordered_combined_averages)

            # Calculate the difference between with PCS and without PCS
            delta_results = calculate_deltas(
                df=reordered_combined_averages, condition_pairs=condition_pairs
            )
            delta_results = apply_htc_and_teq_calculation(df=delta_results)
            logging.info("delta results are calculated.")
            delta_results_with_extracted_info = add_extracted_info_to_dataframe(
                df=delta_results
            )

            logging.info(delta_results)

            # Sort by ID
            delta_results_with_extracted_info = (
                delta_results_with_extracted_info.sort_values(
                    by="PCS_ID", ascending=True
                )
            )

            # Handle missing values
            delta_results_with_extracted_info = (
                delta_results_with_extracted_info.fillna(np.nan)
            )
            logging.info(
                f"delta_results_with_extracted_info: {delta_results_with_extracted_info}"
            )
            logging.info(
                f"columns of delta_results_with_extracted_info: {delta_results_with_extracted_info.columns}"
            )

            # Change spaces to underscores in column names
            delta_results_with_extracted_info = (
                delta_results_with_extracted_info.rename(
                    columns=lambda x: utils.utilities.replace_space_to_underscore(x)
                )
            )

            file_name_to_save = os.path.join(
                Config.DataPaths.PROCESSED_DATA_DIR, "delta_results.csv"
            )
            delta_results_with_extracted_info.to_csv(file_name_to_save, index=False)
            print(f"Saved delta results to {file_name_to_save}")

            # # Extract Teq-related columns and save
            # teq_data = extract_columns(delta_results)
            # file_name_to_save = os.path.join(config.PROCESSED_DATA_DIR, "delta_teq.csv")
            # teq_data.to_csv(file_name_to_save, index=False)
            # print(f"Saved delta results to {file_name_to_save}")

        else:
            logging.info("No averages to save.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
