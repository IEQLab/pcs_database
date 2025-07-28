"""
This code gets all the nessesarely information from this project directory and finally compile them as a database
"""

import pandas as pd
import os
import glob
import utils.utilities as utils
from pandas.core.interchange.dataframe_protocol import DataFrame

from config.configuration import Config


def load_template(template_path):
    """Load the template database for column structure."""
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file {template_path} not found")
    return pd.read_csv(template_path)


def create_empty_database(df_template):
    """Create an empty database with the same columns as the template."""
    return pd.DataFrame(columns=df_template.columns)


# def add_measurements_to_database(df_database, df_measurements):
#     """Add manikin measurements results to the database."""
#     if df_measurements is not None:
#         # Find common columns between the two DataFrames
#         common_columns = set(df_measurements.columns).intersection(
#             set(df_database.columns)
#         )
#
#         # Create a list to store non-empty rows
#         rows_to_append = []
#         for index, row in df_measurements.iterrows():
#             new_row = {col: None for col in df_database.columns}
#             for col in common_columns:
#                 new_row[col] = row[col]
#             # Only add rows that have at least one non-NA value
#             if any(pd.notna(value) for value in new_row.values()):
#                 rows_to_append.append(new_row)
#
#         if rows_to_append:
#             # Create new DataFrame with the same dtypes as the template
#             df_to_append = pd.DataFrame(rows_to_append)
#             # Ensure matching dtypes between the two DataFrames
#             for col in df_database.columns:
#                 if col in df_to_append.columns:
#                     df_to_append[col] = df_to_append[col].astype(df_database[col].dtype)
#
#             df_database = pd.concat([df_database, df_to_append], ignore_index=True)
#
#     return df_database


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


# Merge the clothing data into the database
def add_clothing_data_to_database(
    df_database: DataFrame, df_clothing_processed: DataFrame
) -> DataFrame:
    """Add the single row of clothing data to all rows in the database with IDs 1-20."""
    # Define the range of IDs to update
    target_ids = range(1, 21)

    # Add clothing data to the database for the specified IDs
    for column in df_clothing_processed.columns:
        if column != "PCS_ID":
            df_database.loc[df_database["PCS_ID"].isin(target_ids), column] = (
                df_clothing_processed.iloc[0][column]
            )

    return df_database


def save_database(df_database, output_path):
    """Save the compiled database to a CSV file."""
    df_database.to_csv(output_path, index=False)
    print(f"Database created successfully: {output_path}")


def create_database():
    # Define file paths
    template_path = os.path.join(Config.DataPaths.BASE_DIR, "pcs_database_example.csv")
    measurement_results_path = os.path.join(
        Config.DataPaths.PROCESSED_DATA_DIR, "delta_results.csv"
    )
    clothing_data_path = os.path.join(
        Config.DataPaths.PROCESSED_DATA_DIR, "clothing_measurement_data.csv"
    )
    output_path = os.path.join(Config.DataPaths.BASE_DIR, "pcs_database.csv")

    # Define the dataframes
    df_measurement_results = pd.read_csv(measurement_results_path)
    df_clothing = pd.read_csv(clothing_data_path)
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
    save_database(df_database, output_path)

    return df_database


if __name__ == "__main__":
    create_database()
