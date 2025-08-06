import os
import pandas as pd
from code.config.configuration import Config
from pythermalcomfort.utilities import mean_radiant_tmp, operative_tmp
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


def calculate_to(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate operative temperature (To) using pythermalcomfort based on ISO 7726."""
    required_cols = ["Ta", "MRT", "V"]

    if all(col in df.columns for col in required_cols):
        df["To"] = df.apply(
            lambda row: round(operative_tmp(tdb=row["Ta"], tr=row["MRT"], v=row["V"], standard="ISO"), 2),
            axis=1
        )
        logging.info("Operative temperature (To) calculation completed.")
    else:
        missing = [col for col in required_cols if col not in df.columns]
        logging.warning(f"Operative temperature (To) calculation skipped due to missing columns: {missing}")

    return df


def check_and_fix_rh_values(df: pd.DataFrame, start_date=None, end_date=None, rh_min: float = 0, rh_max: float = 100, replacement_value: float = 50):
    """
    [IMPORTANT] Sometimes measured RH values were abnormal like 10% and 70% after a minute or two
    because of the error of measurement equipment.
    This happened for a period of time.

    This function checks and fixes abnormal RH values within a specified date range and RH value range.
    
    Parameters:
    df: DataFrame with datetime index
    start_date: Start date for checking (format: "YYYY-MM-DD")
    end_date: End date for checking (format: "YYYY-MM-DD")  
    rh_min: Minimum acceptable RH value (default: 0)
    rh_max: Maximum acceptable RH value (default: 100)
    replacement_value: Value to replace abnormal values with (default: 50), or None for NaN
    
    Returns:
    DataFrame with corrected RH values
    """
    if "RH" not in df.columns:
        logging.warning("RH column not found in DataFrame.")
        return df
    
    df_copy = df.copy()
    
    # Filter by date range if specified
    mask = pd.Series(True, index=df_copy.index)
    if start_date is not None:
        mask = mask & (df_copy.index >= start_date)
    if end_date is not None:
        mask = mask & (df_copy.index <= end_date)
    
    # Count total data points in the target range
    total_points_in_range = mask.sum()
    
    # Find abnormal RH values within the date range
    abnormal_mask = mask & ((df_copy["RH"] < rh_min) | (df_copy["RH"] > rh_max) | df_copy["RH"].isna())
    
    # Count abnormal values
    abnormal_count = abnormal_mask.sum()
    
    # Calculate statistics
    valid_rh_mask = mask & df_copy["RH"].notna() & (df_copy["RH"] >= rh_min) & (df_copy["RH"] <= rh_max)
    valid_count = valid_rh_mask.sum()
    
    # Log processing information
    if start_date or end_date:
        date_info = f" within date range {start_date} to {end_date}"
    else:
        date_info = ""
    
    log_message = f"RH data processing summary{date_info}:"
    logging.info(log_message)
    print(log_message)  # Also print to console
    
    log_message = f"  - Total data points in range: {total_points_in_range}"
    logging.info(log_message)
    print(log_message)
    
    log_message = f"  - Valid RH values ({rh_min}% - {rh_max}%): {valid_count}"
    logging.info(log_message)
    print(log_message)
    
    log_message = f"  - Abnormal RH values found: {abnormal_count}"
    logging.info(log_message)
    print(log_message)
    
    if total_points_in_range > 0:
        abnormal_percentage = (abnormal_count / total_points_in_range) * 100
        log_message = f"  - Abnormal data percentage: {abnormal_percentage:.2f}%"
        logging.info(log_message)
        print(log_message)
    
    if abnormal_count > 0:
        # Replace abnormal values
        if replacement_value is None:
            df_copy.loc[abnormal_mask, "RH"] = pd.NA
            log_message = f"  - Action: Replaced {abnormal_count} abnormal RH values with NaN"
            logging.info(log_message)
            print(log_message)
        else:
            df_copy.loc[abnormal_mask, "RH"] = replacement_value
            log_message = f"  - Action: Replaced {abnormal_count} abnormal RH values with {replacement_value}%"
            logging.info(log_message)
            print(log_message)
    else:
        log_message = "  - Action: No replacement needed"
        logging.info(log_message)
        print(log_message)
    
    return df_copy

def reorder_columns(df):
    """Reorder columns for better readability."""
    column_order = ["Ta", "Tg", "Twb", "To", "MRT", "RH", "V", "WBGT", "ET"]
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
    input_file = os.path.join(Config.DataPaths.CHAMBER_DATA_DIR, "Chamber_ThermalEnvironment_RawData.csv")
    output_file = os.path.join(Config.DataPaths.PROCESSED_DATA_DIR, "chamber_thermal_environment.csv")

    df = load_data(file_path=input_file)
    df = filter_valid_dates(df=df)
    df = preprocess_data(df=df)
    df = find_and_rename_columns(df=df)
    df = rename_columns(df=df)
    
    # Check and fix abnormal RH values
    # replace values outside 30-80% range with None
    df = check_and_fix_rh_values(
        df=df, 
        start_date="2025-02-01", 
        end_date="2025-05-31", 
        rh_min=30, 
        rh_max=80, 
        replacement_value=None # or None for NaN
    )
    
    df = calculate_mrt(df=df)
    df = calculate_to(df=df)
    df = reorder_columns(df=df)

    # PLEASE CHANGE THE DATES AS NEEDED
    start_date = "2025-02-01"
    end_date = "2025-05-31"
    df = filter_by_date_range(df=df, start_date=start_date, end_date=end_date)

    df = df.reindex()
    print(df)

    save_data(df=df,output_path=output_file)

    logging.info("Data processing pipeline completed successfully.")

    return df


if __name__ == "__main__":
    main()
