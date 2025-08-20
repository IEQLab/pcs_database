import pandas as pd


def merge_specific_columns_data(
    df: pd.DataFrame, drop_original_data: bool
) -> pd.DataFrame:
    """Merge specific body part columns into groups in order to match the final database format with weights."""
    # Define the body part groups and their weights
    body_part_groups = {
        "Head": (["Crown", "Head"], [0.35, 0.65]),
        "Chest": (["Left_Chest", "Right_Chest"], [0.5, 0.5]),
        "Back": (["Left_Back", "Right_Back", "Back_Side"], [0.28, 0.28, 0.44]),
        "Left_Thigh": (["Left_Front_Thigh", "Left_Back_Thigh"], [0.5, 0.5]),
        "Right_Thigh": (["Right_Front_Thigh", "Right_Back_Thigh"], [0.5, 0.5]),
    }

    # Identify column prefixes (e.g., "Delta_", "PCS_", etc.)
    prefixes = set()
    for col in df.columns:
        for parts, _ in body_part_groups.values():
            for part in parts:
                if col.endswith(part):
                    prefixes.add(col.replace(part, ""))

    # Weighted average the grouped columns
    for group_name, (parts, weights) in body_part_groups.items():
        for prefix in prefixes:
            cols_to_average = [
                prefix + part for part in parts if prefix + part in df.columns
            ]
            if len(cols_to_average) == len(parts):
                # Use a temporary name for the new column (_Merged)
                # This avoids overwriting existing columns and allows for dropping original data if needed
                temp_col_name = f"{prefix}{group_name}_Merged"
                df[temp_col_name] = df[cols_to_average].mul(weights).sum(axis=1) / sum(
                    weights
                )
                if drop_original_data:
                    # Drop the original columns used for the group
                    df = df.drop(columns=cols_to_average)
                # Rename the temporary column to the final name
                df.rename(
                    columns={temp_col_name: f"{prefix}{group_name}"}, inplace=True
                )
    return df
