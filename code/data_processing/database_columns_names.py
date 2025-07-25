"""
This script generates a list of column names for a dataset based on general columns, groups, and mannequin body parts.
It then creates an empty DataFrame with these columns, adds a "Stability" column, and saves the DataFrame to a CSV file.
"""

import pandas as pd
import os
from config.configuration import Config
from code.utils import utilities


def generate_columns(body_parts=utilities.BodyPartLauraOutput):
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
    """Create an empty DataFrame with the specified columns and add a "Stability" column."""
    df = pd.DataFrame(columns=columns)
    df["Stability"] = None  # Add Stability column at the end
    return df


def main():
    columns = generate_columns(body_parts=utilities.BodyPartLauraOutput)
    df = create_dataframe(columns)  # Create an empty DataFrame with these columns

    path_to_save = os.path.join(Config.DataPaths.BASE_DIR, "columns_format.csv")
    df.to_csv(os.path.join(path_to_save), index=False)
    print(f"Columns format saved to {path_to_save}.")


if __name__ == "__main__":
    main()
