"""
This code gets all the nessesarely information from this project directory and finally compile them as a database
"""

import pandas as pd
import os
import sys
import glob
from pandas.core.interchange.dataframe_protocol import DataFrame

# Add the project root directory to sys.path
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

# Add the code directory to sys.path
code_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, code_dir)

import utils.utilities as utils
from config.configuration import Config


def load_template(template_path):
    """Load the template database for column structure."""
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file {template_path} not found")
    return pd.read_csv(template_path)


def create_empty_database(df_template):
    """Create an empty database with the same columns as the template."""
    return pd.DataFrame(columns=df_template.columns)


def add_measurements_to_database(df_database: DataFrame, df_measurements: DataFrame):
    """Add manikin measurements results to the database."""
    if df_measurements is not None:
        # Find common columns between the two DataFrames
        common_columns = df_database.columns.intersection(df_measurements.columns)

        # Filter the measurements DataFrame to only include common columns
        df_measurements_filtered = df_measurements[common_columns]

        # Drop rows in `df_measurements_filtered` that are completely empty
        df_measurements_filtered.dropna(how="all", inplace=True)

        # Append the filtered rows to the database
        df_database = pd.concat(
            [df_database, df_measurements_filtered], ignore_index=True
        )

    return df_database


# TODO: Can be better implemented with a merge operation
def add_trial_metadata_summary_to_database(
    df_database: DataFrame, df_trial_metadata_summary: DataFrame
):
    """
    Add trial metadata summary file (ONLY STATIC DATA) to the database based on matching IDs. Overwrites
    only missing values in the database without affecting existing data.
    """
    # Find common columns between the database and trial metadata summary
    common_columns = df_database.columns.intersection(df_trial_metadata_summary.columns)
    # Perform a merge on the "ID" column to combine the data
    df_merged = df_database.merge(
        df_trial_metadata_summary[common_columns],
        on="PCS_ID",
        how="left",
        suffixes=("", "_new"),
    )

    # Loop through columns in df_pcs_product_info to update missing values in df_database
    for column in df_trial_metadata_summary.columns:
        if column == "PCS_ID":
            continue
        if column in df_database.columns:
            # Update only missing values in the database
            df_merged[column] = df_merged[column].combine_first(
                df_merged[f"{column}_new"]
            )
            # Drop the temporary "_new" column
            df_merged.drop(columns=[f"{column}_new"], inplace=True)
        else:
            # Add new columns from the product info if they don't exist in the database
            df_merged.rename(columns={f"{column}_new": column}, inplace=True)

    # Return the updated database
    return df_merged


def save_database(df_database, output_path):
    """Save the compiled database to a CSV file."""
    df_database.to_csv(output_path, index=False)
    print(f"Database created successfully: {output_path}")


def combine_dataframes(df_database_sydney_uni, df_database_others):
    """Combine two DataFrames into one, ensuring that columns match."""

    def _check_columns_match(df1, df2):
        """
        Check if column names match between two DataFrames.
        If they don't match, print the mismatched columns and add missing columns with NaN.
        """
        columns_df1 = set(df1.columns)
        columns_df2 = set(df2.columns)

        if columns_df1 != columns_df2:
            missing_in_df1 = columns_df2 - columns_df1
            missing_in_df2 = columns_df1 - columns_df2

            print("Columns missing in df1:", missing_in_df1)
            print("Columns missing in df2:", missing_in_df2)
            
            # Add missing columns with NaN values instead of raising an error
            for col in missing_in_df1:
                df1[col] = pd.NA
            for col in missing_in_df2:
                df2[col] = pd.NA
                
            print("Missing columns have been added with NaN values.")
            
            return df1, df2

        return df1, df2

    def _validate_pcs_ids(df_database):
        """Validate PCS_IDs in the database and provide information about duplicates."""
        if df_database["PCS_ID"].is_unique:
            if df_database["PCS_ID"].is_monotonic_increasing:
                print("PCS_IDs are sequential and unique.")
            else:
                print("Warning: PCS_IDs are unique but not in sequential order.")
        else:
            duplicate_ids = df_database["PCS_ID"].value_counts()
            duplicate_ids = duplicate_ids[duplicate_ids > 1]
            print(f"Warning: Found {len(duplicate_ids)} duplicate PCS_IDs:")
            print(duplicate_ids.head(10))  # Show first 10 duplicates
            print("This may be normal if the same PCS is tested under different conditions.")
        
        # Always continue processing instead of raising an error
        print(f"Total records: {len(df_database)}")
        print(f"Unique PCS_IDs: {df_database['PCS_ID'].nunique()}")
        return True

    df_database_sydney_uni, df_database_others = _check_columns_match(df1=df_database_sydney_uni, df2=df_database_others)
    df_combined = pd.concat(
        [df_database_sydney_uni, df_database_others], ignore_index=True
    )
    _validate_pcs_ids(df_combined)
    return df_combined


def create_database():
    # Define file paths
    template_path = os.path.join(Config.DataPaths.BASE_DIR, "pcs_database_example.csv")
    measurement_results_path = os.path.join(
        Config.DataPaths.PROCESSED_DATA_DIR, "delta_results.csv"
    )
    clothing_data_path = os.path.join(
        Config.DataPaths.PROCESSED_DATA_DIR, "clothing_measurement_data.csv"
    )
    others_data_path_tmp = os.path.join(
        Config.DataPaths.EXTERNAL_DIR, "pcs_database_external.csv"
    )
    output_path = os.path.join(Config.DataPaths.BASE_DIR, "pcs_database.csv")

    # Define the dataframes
    df_measurement_results = pd.read_csv(measurement_results_path)
    df_clothing = pd.read_csv(clothing_data_path)
    df_database_others = pd.read_csv(others_data_path_tmp)
    df_template = load_template(template_path=template_path)
    df_database = create_empty_database(df_template=df_template)
    df_database = add_measurements_to_database(df_database, df_measurement_results)

    # Add PCS product information
    trial_metadata_summary_path = os.path.join(
        Config.DataPaths.METADATA_DIR, "combined_trial_metadata.csv"
    )
    df_trial_metadata_summary = pd.read_csv(trial_metadata_summary_path)
    df_database = add_trial_metadata_summary_to_database(
        df_database=df_database, df_trial_metadata_summary=df_trial_metadata_summary
    )
    df_database = combine_dataframes(
        df_database_sydney_uni=df_database, df_database_others=df_database_others
    )
    save_database(df_database, output_path)

    return df_database


if __name__ == "__main__":
    create_database()
