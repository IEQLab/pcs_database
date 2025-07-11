import json
import pandas as pd
import os
from config.configuration import Config


def get_default_values(df: pd.DataFrame) -> dict:
    """Extracts column names and the first row values from a DataFrame as default values."""
    if df.empty:
        raise ValueError("DataFrame is empty. At least one row is required.")
    return df.iloc[0].to_dict()


def validate_dataframe_against_metadata(
    df, metadata: dict, label: str = "DataFrame"
) -> None:
    """Validate DataFrame columns against metadata and print missing/unexpected columns."""
    expected_columns = set()

    # 1. Get top-level column names
    column_props = (
        metadata.get("properties", {}).get("columns", {}).get("properties", {})
    )
    for col, col_meta in column_props.items():
        if "$ref" in col_meta:
            # If reference to body parts, expand with body part names
            if col.endswith("_"):  # e.g., Delta_P_ → Delta_P_Head, etc.
                body_parts = metadata["definitions"]["BodyPart"]["properties"].keys()
                for part in body_parts:
                    expected_columns.add(f"{col}{part}")
        else:
            expected_columns.add(col)

    # 2. Check actual columns
    actual_columns = set(df.columns)

    missing = expected_columns - actual_columns
    unexpected = actual_columns - expected_columns

    if missing:
        print(f"[WARNING] {label} is missing the following expected columns:")
        for col in sorted(missing):
            print(f"  - {col}")
    else:
        print(f"[INFO] {label} includes all expected columns.")

    if unexpected:
        print(f"[INFO] {label} contains unexpected columns not defined in metadata:")
        for col in sorted(unexpected):
            print(f"  + {col}")


def main():
    example_database_file_path = os.path.join(
        Config.DataPaths.BASE_DIR, "pcs_database_example.csv"
    )
    metadata_file_path = os.path.join(Config.DataPaths.BASE_DIR, "metadata.json")

    df_example_database = pd.read_csv(example_database_file_path)

    # Load metadata and your dataframe
    with open(metadata_file_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    validate_dataframe_against_metadata(
        df=df_example_database, metadata=metadata, label="DeltaResults"
    )


if __name__ == "__main__":
    main()
