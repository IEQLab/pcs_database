import os
import numpy as np
import pandas as pd
import chardet
from datetime import timedelta
import re
from collections import defaultdict
import configuration as config
import utilities
import create_columns_format


# Step 1: Detect file encoding
def detect_encoding(file_path):
    """
    Detect the file encoding using chardet.
    """
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        return chardet.detect(raw_data)['encoding']


# Step 2: Load CSV file
def load_data_with_custom_columns(file_path, custom_columns):
    """
    Load CSV file and apply custom columns format.

    Args:
        file_path (str): Path to the CSV file.
        custom_columns (list): List of custom column names.
    Returns:
        pd.DataFrame: Loaded DataFrame with custom columns.
    """
    # Detect encoding and load data
    encoding = detect_encoding(file_path)
    df = pd.read_csv(
        file_path,
        encoding=encoding,
        skiprows=5,  # Skip unnecessary rows
        header=None
    )

    # Remove unnecessary columns and assign custom column names
    # Remove the rightmost column only if it is empty
    if df.iloc[:, -1].isnull().all():
        df = df.iloc[:, :-1]

    df.columns = custom_columns

    # Convert 'Datetime' column and set it as index
    df["Datetime"] = pd.to_datetime(df["Datetime"], format="%d/%m/%Y %I:%M:%S %p", errors='coerce')
    df.set_index("Datetime", inplace=True)

    return df


# Step 3: Calculate averages for the last minute of data
def average_last_five_minute(file_path, custom_columns):
    """
    Calculate averages for the last five minute of data.

    Args:
        file_path (str): Path to the CSV file.
        custom_columns (list): List of custom column names.
    Returns:
        pd.DataFrame: DataFrame containing averages and additional information.
    """
    df = load_data_with_custom_columns(file_path, custom_columns)

    # Get
    last_five_minute_start = df.index.max() - pd.Timedelta(minutes=5)
    last_five_minute_data = df[df.index > last_five_minute_start]

    if not last_five_minute_data.empty:
        # Calculate averages and round to 2 decimal places
        averages = last_five_minute_data.mean().to_frame().T
        averages["Reference_time"] = last_five_minute_data.index.mean().strftime("%Y-%m-%d %H:%M:%S") # remove milliseconds
        averages["File_name"] = os.path.basename(file_path)
        averages.set_index('File_name', inplace=True)
        return averages

    return None


# Step 4: Search for files by keyword
import os

import os


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
            os.path.join(root, file)
            for file in files if keyword in file
        )

    return result_files


def extract_info_from_filename(filename):
    """
    Extracts ID, Name, Level, Ta, and Control method from a given filename.
    Additionally extracts optional parameters like Angle and Distance if present.
    """
    # Remove file extension
    filename = os.path.basename(filename).split('.')[0]

    # Split by underscores
    parts = filename.split('_')

    # Initialize extracted data
    dict_extracted_info = {
        "ID": None,
        "PCS_name": None,
        "Intensity": None,
        "Angle": None,
        "Distance": None,
        "Ta": None,
        "Control method": None
    }

    # Extract known fixed fields
    dict_extracted_info["ID"] = int(parts[1].replace("ID", ""))  # Extract number only
    dict_extracted_info["PCS_name"] = parts[2]
    dict_extracted_info["Level"] = parts[3]

    # Process remaining parts for optional parameters
    for part in parts[4:]:
        if part.startswith("Angle"):
            dict_extracted_info["Angle"] = int(part.replace("Angle", ""))
        elif part.startswith("Distance"):
            dict_extracted_info["Distance"] = int(part.replace("Distance", ""))
        elif part.startswith("Ta"):
            dict_extracted_info["Ta"] = int(part.replace("Ta", ""))
        elif "Control" in part:  # if "Control" is in the part
            dict_extracted_info["Control method"] = part

    print(dict_extracted_info)

    return dict_extracted_info


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

        # Store extracted data along with original row, placing extracted info first
        extracted_data.append({
            **row.to_dict(),  # Add original delta values first
            "ID": with_pcs_info["ID"],
            "PCS_name": with_pcs_info["PCS_name"],
            "Level": with_pcs_info["Level"],
            "Angle": with_pcs_info["Angle"],
            "Distance": with_pcs_info["Distance"],
            "Ta": with_pcs_info["Ta"],
            "Control method": with_pcs_info["Control method"],
        })

    # Convert list of dictionaries to DataFrame
    updated_df = pd.DataFrame(extracted_data)

    # Reorder columns to ensure extracted info is at the left
    extracted_columns = ["ID", "PCS_name", "Level", "Angle", "Distance", "Ta", "Control method"]
    remaining_columns = [col for col in updated_df.columns if col not in extracted_columns]

    # Reorder DataFrame
    updated_df = updated_df[extracted_columns + remaining_columns]

    return updated_df


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
    new_columns_list = create_columns_format.generate_columns(body_parts=utilities.BodyPart)

    # Ensure only existing columns are selected
    ordered_columns = [col for col in new_columns_list if col in df.columns]

    # Ensure 'Reference_time' is included at the end
    if "Reference_time" in df.columns:
        ordered_columns.append("Reference_time")  # Add it explicitly

    return df[ordered_columns]

# Step 6: Calculate delta between conditions
def calculate_deltas(df, condition_pairs):
    """
    Compute the difference (delta) between condition pairs while preserving Reference_time.

    Args:
        df (pd.DataFrame): DataFrame containing averaged sensor data.
        condition_pairs (list of tuples): List of (with_PCS, without_PCS) condition pairs.

    Returns:
        pd.DataFrame: DataFrame containing delta values for P_ columns and Reference_time.
    """
    results = []

    # Ensure 'File_name' exists in the DataFrame
    if 'File_name' not in df.columns:
        df = df.reset_index()

    # Extract only columns containing 'P_', excluding GroupA and GroupB
    keyword = "P_"
    exclude_keywords = ["GroupA", "GroupB"]
    p_columns = [col for col in df.columns if col.startswith(keyword) and not any(ex in col for ex in exclude_keywords)]

    # Ensure Reference_time is included if it exists in the DataFrame
    if "Reference_time" in df.columns:
        p_columns.append("Reference_time")

    for condition_without_pcs, condition_with_pcs in condition_pairs:
        # Find matching rows for each condition using File_name
        matched_files_without_pcs = df["File_name"].str.contains(condition_without_pcs, case=False, na=False, regex=False)
        matched_files_with_pcs = df["File_name"].str.contains(condition_with_pcs, case=False, na=False, regex=False)

        if matched_files_with_pcs.any() and matched_files_without_pcs.any():
            # Extract the first matching row for each condition
            row_condition_without_pcs = df.loc[matched_files_without_pcs, p_columns].iloc[0]
            row_condition_with_pcs = df.loc[matched_files_with_pcs, p_columns].iloc[0]

            # Identify numeric columns (excluding Reference_time)
            numeric_columns = [col for col in p_columns if col != "Reference_time"]

            # Convert numerical columns to float
            row_condition_without_pcs[numeric_columns] = row_condition_without_pcs[numeric_columns].astype(float)
            row_condition_with_pcs[numeric_columns] = row_condition_with_pcs[numeric_columns].astype(float)

            # Compute deltas (difference between with_PCS and without_PCS)
            delta_values = (row_condition_without_pcs[numeric_columns] - row_condition_with_pcs[numeric_columns]).round(2)

            # Ensure Reference_time is preserved without modification
            reference_time_value = row_condition_with_pcs["Reference_time"] if "Reference_time" in p_columns else None

            # Rename columns to add 'Delta_' prefix (excluding Reference_time)
            prefix = "Delta"
            delta_values = delta_values.rename(lambda col: f"{prefix}_{col}" if col != "Reference_time" else col)

            # Store results as a DataFrame row
            delta_values["Condition_without_PCS"] = condition_without_pcs
            delta_values["Condition_with_PCS"] = condition_with_pcs

            # Convert results to DataFrame and reorder columns
            delta_df = pd.DataFrame([delta_values])

            # Ensure Reference_time is the first column
            if "Reference_time" in p_columns:
                delta_df.insert(0, "Reference_time", reference_time_value)

            results.append(delta_df)

    # Combine all results into a single DataFrame
    return pd.concat(results, ignore_index=True) if results else pd.DataFrame()



# Main function
def main():
    """
    Main function to process all matching files and calculate averages.
    """
    try:
        # Load column format
        columns_format_file = os.path.join(config.DATA_DIR, "columns_format.csv")
        columns_format = pd.read_csv(columns_format_file).columns.tolist()

        # Find all target files
        keyword = "TskControl"
        matching_files = find_files_with_keyword(folder_path=config.RAW_DATA_DIR, keyword=keyword, exclude_folders=["Old", "UFAD"])
        print("matching_files", matching_files)
        if not matching_files:
            print(f"No files found with the keyword {keyword}")
            return

        # Generate condition pairs based on date
        condition_pairs = generate_condition_pairs(matching_files=matching_files)
        print(f"Generated condition pairs: {condition_pairs}")

        # Process each file
        all_averages = []
        for file_path in matching_files:
            print(f"Processing file: {file_path}")
            averages = average_last_five_minute(file_path=file_path, custom_columns=columns_format)
            if averages is not None:
                all_averages.append(averages)
            else:
                print(f"No valid data found in the last minute for file: {file_path}")

        # Combine and save results if there is data
        if all_averages:
            combined_averages = pd.concat(all_averages)
            # print("combined_averages:", combined_averages)

            # Reorder
            reordered_combined_averages = reorder_columns(df=combined_averages)
            # print("reordered_combined_averages:", reordered_combined_averages)

            # Summary of average data of each file
            file_name_to_save = os.path.join(config.PROCESSED_DATA_DIR, "all_average_data.csv")
            reordered_combined_averages.to_csv(file_name_to_save)
            print(f"Saved averaged results of each file to {file_name_to_save}")

            # Calculate the difference between with PCS and without PCS
            delta_results = calculate_deltas(df=reordered_combined_averages, condition_pairs=condition_pairs)
            delta_results_with_extracted_info = add_extracted_info_to_dataframe(df=delta_results)

            # Sort by ID
            delta_results_with_extracted_info = delta_results_with_extracted_info.sort_values(by="ID", ascending=True)

            # Handle missing values
            delta_results_with_extracted_info = delta_results_with_extracted_info.fillna(np.nan)

            print("delta_results:", delta_results_with_extracted_info)
            file_name_to_save = os.path.join(config.PROCESSED_DATA_DIR, "delta_results.csv")
            delta_results_with_extracted_info.to_csv(file_name_to_save, index=False)
            print(f"Saved delta results to {file_name_to_save}")

            # # Extract Teq-related columns and save
            # teq_data = extract_columns(delta_results)
            # file_name_to_save = os.path.join(config.PROCESSED_DATA_DIR, "delta_teq.csv")
            # teq_data.to_csv(file_name_to_save, index=False)
            # print(f"Saved delta results to {file_name_to_save}")

        else:
            print("No averages to save.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
