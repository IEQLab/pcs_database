import os
import sys
import pandas as pd
import yaml

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, project_root)

from code.config.configuration import Config


def load_metadata_relations(path: str) -> dict:
    with open(path, "r") as file:
        return yaml.safe_load(file)


def combine_metadata(
    base_path: str, trial_table_name: str, metadata_file: str
) -> pd.DataFrame:
    relations = load_metadata_relations(os.path.join(base_path, metadata_file))
    trial_df = pd.read_csv(os.path.join(base_path, f"{trial_table_name}.csv"))

    # Merge trial data with related tables
    for related_table, fk_column in (
        relations[trial_table_name].get("foreign_keys", {}).items()
    ):
        related_df = pd.read_csv(os.path.join(base_path, f"{related_table}.csv"))
        trial_df = trial_df.merge(
            related_df,
            how="left",
            left_on=fk_column,
            right_on=relations[related_table]["primary_key"],
            suffixes=("_trial", f"_{related_table}"),
        )

    # Add pcs_product_info.csv and reorder columns
    pcs_info = pd.read_csv(os.path.join(base_path, "pcs_product_info.csv"))
    trial_df = trial_df.merge(pcs_info, how="left", on="PCS_ID", suffixes=("", "_pcs"))

    # Reorder columns to match the desired order
    required_columns = list(pcs_info.columns) + ["Experiment_ID", "Manikin_ID"]
    columns_order = required_columns + [
        col for col in trial_df.columns if col not in required_columns
    ]

    return trial_df[columns_order]


def main():
    base_path = Config.DataPaths.METADATA_DIR
    trial_table_name = "trial_info"
    metadata_file = "metadata_relations.yaml"

    combined_df = combine_metadata(base_path, trial_table_name, metadata_file)
    output_path = os.path.join(base_path, "combined_trial_metadata.csv")
    combined_df.to_csv(output_path, index=False)
    print(f"✅ Combined metadata CSV saved successfully to: {output_path}")


if __name__ == "__main__":
    main()
