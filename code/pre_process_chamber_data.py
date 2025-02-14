import os
import pandas as pd
import numpy as np
import configuration as config
from datetime import datetime
from pythermalcomfort.utilities import mean_radiant_tmp
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_data(file_path):
    """Load CSV file and set appropriate column headers."""
    try:
        df = pd.read_csv(file_path, header=None)
        df.columns = df.iloc[11]  # Use the 11th row as headers
        df = df[12:].reset_index(drop=True)
        logging.info("Data loaded successfully from %s", file_path)
        return df
    except Exception as e:
        logging.error("Error loading data: %s", e)
        raise


def filter_valid_dates(df, date_col="Session name:"):
    """Filter out rows where the session name is not a valid date."""
    date_format = "%A, %d %B %Y"  # Example: "Friday, 24 January 2025"
    df = df[pd.to_datetime(df[date_col], format=date_format, errors='coerce').notna()]
    logging.info("Filtered rows with invalid dates in column '%s'", date_col)
    return df


def preprocess_data(df):
    """Preprocess data by selecting relevant columns and converting types."""
    selected_columns = ["Session name:", "Time:", "Temperature", "Relative Humidity", "WBGT", "Air Velocity",
                        "Effective Temperature"]
    df_selected = df[selected_columns].copy()

    # Create a combined datetime column
    df_selected["Datetime"] = pd.to_datetime(df_selected["Session name:"].astype(str) + " " + df_selected["Time:"],
                                             errors='coerce')
    df_selected = df_selected.set_index("Datetime").drop(columns=["Session name:", "Time:"])

    # Convert all columns to numeric
    df_selected = df_selected.apply(pd.to_numeric, errors="coerce")
    logging.info("Preprocessing complete: Converted data types and created Datetime index.")
    return df_selected


def find_and_rename_columns(df):
    """Find and rename WBGT and Temperature columns."""
    df_wbgt_columns = [i for i, col in enumerate(df.columns) if "WBGT" in str(col)]
    df_temperature_columns = [i for i, col in enumerate(df.columns) if "Temperature" in str(col)]

    if len(df_wbgt_columns) >= 4:
        df.columns.values[df_wbgt_columns[0]] = "Twb"
        df.columns.values[df_wbgt_columns[1]] = "Tg"
        df.columns.values[df_wbgt_columns[2]] = "Ta"
        df.columns.values[df_wbgt_columns[3]] = "WBGT"
        df = df.drop(columns=["Ta"], errors='ignore')

    if len(df_temperature_columns) >= 2:
        df.columns.values[df_temperature_columns[0]] = "Ta"
        df.columns.values[df_temperature_columns[1]] = "To"
        df = df.drop(columns=["To"], errors='ignore')

    logging.info("Renamed WBGT and Temperature columns where applicable.")
    return df


def filter_by_date_range(df, start_date, end_date):
    """Filter data within the specified date range."""
    df_filtered = df[(df.index >= start_date) & (df.index <= end_date)]
    logging.info("Filtered data between %s and %s", start_date, end_date)
    return df_filtered


def rename_columns(df):
    """Rename columns for consistency."""
    rename_dict = {
        "Relative Humidity": "RH",
        "Air Velocity": "V",
        "Effective Temperature": "ET"
    }
    df = df.rename(columns=rename_dict)
    logging.info("Columns renamed successfully.")
    return df


def calculate_mrt(df):
    # print(df.columns)
    """Calculate Mean Radiant Temperature (MRT)."""
    if all(col in df.columns for col in ["Tg", "Ta", "V"]):
        df["MRT"] = df.apply(
            lambda row: mean_radiant_tmp(tg=row["Tg"], tdb=row["Ta"], v=row["V"], d=0.15, emissivity=0.95,
                                         standard="ISO"), axis=1)
        logging.info("MRT calculation completed.")
    else:
        logging.warning("MRT calculation skipped due to missing columns.")
    return df


def reorder_columns(df):
    """Reorder columns for better readability."""
    column_order = ["Ta", "Tg", "Twb", "MRT", "RH", "V", "WBGT", "ET"]
    df = df[[col for col in column_order if col in df.columns]]
    logging.info("Columns reordered for readability.")
    return df


def save_data(df, output_path):
    """Save processed data to a CSV file."""
    try:
        df.to_csv(output_path)
        logging.info("Processed data saved successfully to %s", output_path)
    except Exception as e:
        logging.error("Error saving data: %s", e)
        raise


def main():
    """Main function to process chamber thermal environment data."""
    input_file = os.path.join(config.CHAMBER_DATA_DIR, "Chamber_ThermalEnvironment_RawData.csv")
    output_file = os.path.join(config.PROCESSED_DATA_DIR, "chamber_thermal_environment.csv")

    df = load_data(file_path=input_file)
    df = filter_valid_dates(df=df)
    df = preprocess_data(df=df)
    df = find_and_rename_columns(df=df)
    df = rename_columns(df=df)
    df = calculate_mrt(df=df)
    df = reorder_columns(df=df)

    # PLEASE CHANGE THE DATES AS NEEDED
    start_date = "2025-02-01"
    end_date = "2025-02-14"
    df = filter_by_date_range(df=df, start_date=start_date, end_date=end_date)

    save_data(df=df,output_path=output_file)

    logging.info("Data processing pipeline completed successfully.")


if __name__ == "__main__":
    main()

# import os
# import numpy as np
# import pandas as pd
# import chardet
# from datetime import timedelta
# import re
# from collections import defaultdict
# import configuration as config
# from pythermalcomfort.utilities import mean_radiant_tmp
#
# # Load the CSV file
# # test_file_path = os.path.join(config.CHAMBER_DATA_DIR, "2025-02-11_Chamber_Thermal_Environment.csv")
# test_file_path = os.path.join(config.CHAMBER_DATA_DIR, "Chamber_ThermalEnvironment_RawData.csv")
# df = pd.read_csv(test_file_path, header=None)
#
# # Set the 11th row as column names
# df.columns = df.iloc[11]
# df = df[12:].reset_index(drop=True)
#
# # Check the columns called "Session name:" and filter data with nondatetime data
# date_format = "%A, %d %B %Y"  # 例: "Friday, 24 January 2025"
# df = df[pd.to_datetime(df["Session name:"], format=date_format, errors='coerce').notna()]
#
#
# # # Convert all columns (except index) to numeric
# # df_new = df_new.apply(pd.to_numeric, errors="coerce")
#
# # Select necessary columns
# selected_columns = ["Session name:", "Time:", "Temperature", "Relative Humidity", "WBGT", "Air Velocity", "Effective Temperature"]
# df_selected = df[selected_columns].copy()
#
# # Create "Datetime" column by combining "Session name:" and "Time:" and convert to datetime type
# df_selected["Datetime"] = df_selected["Session name:"].astype(str) + " " + df_selected["Time:"].astype(str)
# df_selected["Datetime"] = pd.to_datetime(df_selected["Datetime"], errors='coerce')
#
# # Set "Datetime" as index and remove unnecessary columns
# df_selected = df_selected.set_index("Datetime").drop(columns=["Session name:", "Time:"])
#
# # Convert all columns (except index) to numeric
# df_selected = df_selected.apply(pd.to_numeric, errors="coerce")
#
# # Find and rename WBGT columns
# df_wbgt_columns = [i for i, col in enumerate(df_selected.columns) if "WBGT" in str(col)]
# df_temperature_columns = [i for i, col in enumerate(df_selected.columns) if "Temperature" in str(col)]
#
# if len(df_wbgt_columns) >= 4:
#     df_selected.columns.values[df_wbgt_columns[0]] = "Twb"
#     df_selected.columns.values[df_wbgt_columns[1]] = "Tg"
#     df_selected.columns.values[df_wbgt_columns[2]] = "Ta"
#     df_selected.columns.values[df_wbgt_columns[3]] = "WBGT"
#     df_selected = df_selected.drop(columns=["Ta"], errors='ignore')
#
# if len(df_temperature_columns) >= 2:
#     df_selected.columns.values[df_temperature_columns[0]] = "Ta"
#     df_selected.columns.values[df_temperature_columns[1]] = "To"
#     df_selected = df_selected.drop(columns=["To"], errors='ignore')
#
# # Rename the specified columns
# rename_dict = {
#     "Relative Humidity": "RH",
#     "Air Velocity": "V",
#     "Effective Temperature": "ET"
# }
# df_selected = df_selected.rename(columns=rename_dict)
#
# # Calculate Mean Radiant Temperature (MRT) using pythermalcomfort
# df_selected["MRT"] = df_selected.apply(lambda row: mean_radiant_tmp(
#     tg=row["Tg"], tdb=row["Ta"], v=row["V"], d=0.15, emissivity=0.95, standard="ISO"), axis=1)
#
# # Reorder the columns for better readability
# order = ["Ta", "Tg", "Twb", "MRT", "RH", "V", "WBGT", "ET"]
# df_selected = df_selected[order]
#
# # Save processed data
# df_selected.to_csv(os.path.join(config.PROCESSED_DATA_DIR, "chamber_thermal_environment.csv"))