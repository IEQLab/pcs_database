"""
This script generates a list of column names for a dataset based on general columns, groups, and mannequin body parts.
It then creates an empty DataFrame with these columns, adds a "Stability" column, and saves the DataFrame to a CSV file.
"""

import pandas as pd
import os
from config.configuration import Config
from code.utils import utilities


def generate_columns(body_parts=utilities.BodyPartTemporary):
    """
    Generate a list of column names for the dataset based on general columns, groups, and mannequin body parts.
    Returns:
        list: List of all column names.
    """

    # General columns and group definitions
    general_columns = ["Datetime", "Runtime"]
    group_columns = ["All", "Group A", "Group B"]
    group_results = ["Tsk", "P", "Clo", "Teq", "PMV", "PPD", "SET", "ET"]
    part_results = ["Tsk", "P", "Clo", "Teq"]

    # Generate group columns in "item_body" order
    group_columns_full = [
        f"{result}_{group}" for group in group_columns for result in group_results
    ]

    # Extract body part names from BodyPartTemporary dataclass
    body_part_columns = [
        value for key, value in vars(body_parts).items() if not key.startswith("__")
    ]
    manikin_columns_full = [
        f"{result}_{part}" for part in body_part_columns for result in part_results
    ]

    # Combine all columns
    all_columns = general_columns + group_columns_full + manikin_columns_full
    return all_columns


def create_dataframe(columns):
    """
    Create an empty DataFrame with the specified columns and add a "Stability" column.

    Args:
        columns (list): List of column names for the DataFrame.
    Returns:
        DataFrame: Empty DataFrame with the specified columns.
    """
    df = pd.DataFrame(columns=columns)
    df["Stability"] = None  # Add Stability column at the end
    return df


def save_dataframe_to_csv(df, file_path):
    """
    Save DataFrame to a CSV file, creating the directory if it doesn't exist.

    Args:
        df (DataFrame): The DataFrame to save.
        file_path (str): Path to save the CSV file.
    """
    os.makedirs(
        os.path.dirname(file_path), exist_ok=True
    )  # Ensure the directory exists
    df.to_csv(file_path, index=False)
    print(f"DataFrame successfully saved to {file_path}")


def main():
    """
    Main function to generate the DataFrame and save it as a CSV file.
    """
    # Generate all column names
    columns = generate_columns(body_parts=utilities.BodyPartTemporary)

    # For debugging/development purposes
    # tmp_columns = generate_columns(body_parts=utilities.BodyPart)
    # print(tmp_columns)

    # Create an empty DataFrame with these columns
    df = create_dataframe(columns)

    # Define the output file path and save the DataFrame to a CSV file
    output_file = os.path.join(Config.DataPaths.BASE_DIR, "columns_format.csv")
    save_dataframe_to_csv(df, output_file)


if __name__ == "__main__":
    main()
