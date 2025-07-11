"""
This code gets all the nessesarely information from this project directory and finally compile them as a database
"""

import pandas as pd
import os
import glob
from config.configuration import Config


def load_template(template_path):
    """Load the template database for column structure."""
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file {template_path} not found")
    return pd.read_csv(template_path)


def create_empty_database(df_template):
    """Create an empty database with the same columns as the template."""
    return pd.DataFrame(columns=df_template.columns)


def add_measurements_to_database(df_database, measurements_path):
    """Add manikin measurements results to the database."""
    if os.path.exists(measurements_path):
        df_measurements = pd.read_csv(measurements_path)
        # Only add values for columns that exist in both dataframes
        common_columns = set(df_measurements.columns).intersection(
            set(df_database.columns)
        )

        # Create a list to store non-empty rows
        rows_to_append = []
        for index, row in df_measurements.iterrows():
            new_row = {col: None for col in df_database.columns}
            for col in common_columns:
                new_row[col] = row[col]
            # Only add rows that have at least one non-NA value
            if any(pd.notna(value) for value in new_row.values()):
                rows_to_append.append(new_row)

        if rows_to_append:
            # Create new DataFrame with the same dtypes as the template
            df_to_append = pd.DataFrame(rows_to_append)
            # Ensure matching dtypes between the two DataFrames
            for col in df_database.columns:
                if col in df_to_append.columns:
                    df_to_append[col] = df_to_append[col].astype(df_database[col].dtype)

            df_database = pd.concat([df_database, df_to_append], ignore_index=True)

    return df_database


def add_pcs_information_to_database(df_database, pcs_files):
    """Add PCS information to the database."""
    for pcs_file in pcs_files:
        if os.path.exists(pcs_file):
            df_pcs = pd.read_csv(pcs_file)
            # Map PCS data to database
            # Customization needed based on actual data structure
            # Example: df_database = merge_pcs_data(df_database, df_pcs)
    return df_database


def save_database(df_database, output_path):
    """Save the compiled database to a CSV file."""
    df_database.to_csv(output_path, index=False)
    print(f"Database created successfully: {output_path}")


def create_database():
    template_path = os.path.join(Config.DataPaths.BASE_DIR, "pcs_database_example.csv")
    measurements_path = os.path.join(
        Config.DataPaths.PROCESSED_DATA_DIR, "delta_results.csv"
    )
    output_path = os.path.join(Config.DataPaths.BASE_DIR, "pcs_database.csv")

    df_template = load_template(template_path)
    df_database = create_empty_database(df_template)
    df_database = add_measurements_to_database(df_database, measurements_path)
    save_database(df_database, output_path)

    return df_database


if __name__ == "__main__":
    create_database()
