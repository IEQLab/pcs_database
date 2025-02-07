import os
import pandas as pd
import chardet
from datetime import timedelta
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
    data = pd.read_csv(
        file_path,
        encoding=encoding,
        skiprows=5,  # Skip unnecessary rows
        header=None
    )

    # Remove unnecessary columns and assign custom column names
    # Remove the rightmost column only if it is empty
    if data.iloc[:, -1].isnull().all():
        data = data.iloc[:, :-1]

    data.columns = custom_columns

    # Convert 'Datetime' column and set it as index
    data["Datetime"] = pd.to_datetime(data["Datetime"], format="%d/%m/%Y %I:%M:%S %p", errors='coerce')
    data.set_index("Datetime", inplace=True)

    return data


# Step 3: Calculate averages for the last minute of data
def average_last_minute(file_path, custom_columns):
    """
    Calculate averages for the last minute of data.

    Args:
        file_path (str): Path to the CSV file.
        custom_columns (list): List of custom column names.
    Returns:
        pd.DataFrame: DataFrame containing averages and additional information.
    """
    df = load_data_with_custom_columns(file_path, custom_columns)
    last_minute_start = df.index.max() - pd.Timedelta(minutes=1)
    last_minute_data = df[df.index > last_minute_start]

    if not last_minute_data.empty:
        # Calculate averages and round to 2 decimal places
        averages = last_minute_data.mean().to_frame().T
        averages['Representative_time'] = last_minute_data.index.mean()
        averages['File_name'] = os.path.basename(file_path)
        averages.set_index('File_name', inplace=True)
        return averages

    return None


# Step 4: Search for files by keyword
def find_files_with_keyword(folder_path, keyword):
    """
    Search for files in a folder containing a specific keyword in their names.
    """
    return [
        os.path.join(root, file)
        for root, _, files in os.walk(folder_path)
        for file in files if keyword in file
    ]

# Step 5: Reorder columns based on the BodyPart dataclass
def reorder_columns(data):
    """
    Reorder the columns of a DataFrame based on the BodyPart dataclass.
    As output file format from the manikin is fixed, we need to change the columns order to understand easily.
    """
    new_columns_list = create_columns_format.generate_columns(body_parts=utilities.BodyPart)
    ordered_data = data[[col for col in new_columns_list if col in data.columns]]
    return ordered_data


# Step 6: Calculate delta between conditions
def calculate_deltas(data, condition_pairs):
    results = []

    # Reset index to ensure 'File_name' is a column
    if 'File_name' not in data.columns:
        data = data.reset_index()

    for condition1, condition2 in condition_pairs:
        rows_condition1 = data[data["File_name"].str.contains(condition1, case=False, na=False)]
        rows_condition2 = data[data["File_name"].str.contains(condition2, case=False, na=False)]

        if not rows_condition1.empty and not rows_condition2.empty:
            mean_condition1 = rows_condition1.mean(numeric_only=True)
            mean_condition2 = rows_condition2.mean(numeric_only=True)

            # Compute the delta and round the final result to 2 decimal places
            delta_values = (mean_condition2 - mean_condition1).round(2)
            delta_values["Condition1"] = condition1
            delta_values["Condition2"] = condition2

            # Add "Delta_" prefix to all columns except 'Condition1' and 'Condition2'
            # Columns to exclude from the renaming proces
            excluded_columns = ["Condition1", "Condition2"]
            delta_values = delta_values.rename(
                {col: f"Delta_{col}" for col in delta_values.index if col not in excluded_columns}
            )

            results.append(delta_values)

    return pd.DataFrame(results)


def extract_teq_columns(data):
    # Identify columns containing 'Teq' or the specific condition columns
    target_columns = [col for col in data.columns if 'Teq' in col] + ["Condition1", "Condition2"]

    # Extract the relevant columns
    extracted_data = data[target_columns]

    return extracted_data

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
        matching_files = find_files_with_keyword(config.RAW_DATA_DIR, "ComfortControl")
        if not matching_files:
            print("No files found with the keyword 'ComfortControl'")
            return

        # Process each file
        all_averages = []
        for file_path in matching_files:
            print(f"Processing file: {file_path}")
            averages = average_last_minute(file_path, custom_columns=columns_format)
            if averages is not None:
                all_averages.append(averages)
                print(averages)
            else:
                print(f"No valid data found in the last minute for file: {file_path}")

        # Combine and save results if there is data
        if all_averages:
            combined_averages = pd.concat(all_averages)

            # Reorder
            reordered_combined_averages = reorder_columns(combined_averages)

            file_name_to_save = os.path.join(config.PROCESSED_DATA_DIR, "all_average_data.csv")
            reordered_combined_averages.to_csv(file_name_to_save)
            print(f"Saved averaged results of each file to {file_name_to_save}")

            # Define condition pairs and calculate deltas
            condition_pairs = [
                ("withoutPCS_Ta25", "Daison_Fan_Level2_Ta25"),
                ("withoutPCS_Ta25", "Daison_Fan_Level4_Ta25"),
                ("withoutPCS_Ta25", "Daison_Fan_Level6_Ta25"),
                ("withoutPCS_Ta25", "Neck_Fan_Level1_Ta25"),
                ("withoutPCS_Ta25", "Neck_Fan_Level3_Ta25"),
                ("withoutPCS_Ta25", "Neck_Fan_Level4_Ta25"),
            ]
            delta_results = calculate_deltas(data=reordered_combined_averages, condition_pairs=condition_pairs)
            file_name_to_save = os.path.join(config.PROCESSED_DATA_DIR, "delta_results.csv")
            delta_results.to_csv(file_name_to_save, index=False)
            print(f"Saved delta results to {file_name_to_save}")

            # Extract Teq-related columns and save
            teq_data = extract_teq_columns(delta_results)
            file_name_to_save = os.path.join(config.PROCESSED_DATA_DIR, "delta_teq.csv")
            teq_data.to_csv(file_name_to_save, index=False)
            print(f"Saved delta results to {file_name_to_save}")

        else:
            print("No averages to save.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
