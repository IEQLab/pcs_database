import os
import pandas as pd
from config.configuration import Config
from preprocess_manikin import (
    average_last_five_minute,
    reorder_columns,
    match_nearest_datetime,
)
import preprocess_chamber
from calc_clothing_insulation import calc_intrinsic_clothing_insulation
import utils.utilities as utils

# Config
columns_format_file = os.path.join(Config.DataPaths.BASE_DIR, "columns_format.csv")
columns_format = pd.read_csv(columns_format_file).columns.tolist()

df_chamber = preprocess_chamber.main()

# File paths
nude_file_path = os.path.join(
    Config.DataPaths.CLOTHING_DATA_DIR,
    "2025-05-09_ClothingMeasurement_Ta21_TskControl34_Nude.csv",
)
summer_clothing_file_path = os.path.join(
    Config.DataPaths.CLOTHING_DATA_DIR,
    "2025-05-09_ClothingMeasurement_Ta21_TskControl34_SummerClothing.csv",
)
winter_clothing_file_path = os.path.join(
    Config.DataPaths.CLOTHING_DATA_DIR,
    "2025-05-08_ClothingMeasurement_Ta21_TskControl34_WinterClothing.csv",
)


# Dataframes
def load_and_process_data(file_path, columns_format):
    """Average the data for the last 5 min and reorder the columns"""
    df = average_last_five_minute(file_path, columns_format)
    df_reordered = reorder_columns(df)
    df_reordered_with_chamber_data = match_nearest_datetime(
        df_manikin=df_reordered, df_chamber=df_chamber
    )
    return df_reordered_with_chamber_data


df_nude = load_and_process_data(file_path=nude_file_path, columns_format=columns_format)
df_summer = load_and_process_data(
    file_path=summer_clothing_file_path, columns_format=columns_format
)
df_winter = load_and_process_data(
    file_path=winter_clothing_file_path, columns_format=columns_format
)
# df_nude = match_nearest_datetime(df_nude, df_chamber)

print(f"df_winter:{df_winter.columns}")

# Change format to match the metadata


def change_df_format_to_match_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess clothing data into a flattened format with Clo_{BodyPart}
    as columns and corresponding 'Icl' values, grouped by Clothing_ID."""

    # Group by Clothing_ID and process each group
    processed_dfs = []
    for clothing_id, group_df in df.groupby("Clothing_ID"):
        # Pivot the data on 'BodyPart' to transpose rows into columns
        group_df = (
            group_df[["BodyPart", "Icl"]].drop_duplicates().set_index("BodyPart").T
        )

        # Add 'Clo_' prefix to the columns
        group_df.columns = [f"Clo_{col}" for col in group_df.columns]

        # Replace underscores with spaces in column names
        group_df.columns = [
            utils.replace_space_to_underscore(col) for col in group_df.columns
        ]

        # Add Clothing_ID as the index
        group_df["Clothing_ID"] = clothing_id
        group_df = group_df.set_index("Clothing_ID")

        processed_dfs.append(group_df)

    # Combine all processed groups into a single DataFrame
    final_df = pd.concat(processed_dfs)
    return final_df


def main():
    t_o_fixed = 21.0

    def is_valid_body_part(col):
        """Excludes column names having "Group A" and "Group B"""
        return (
            col.startswith("Tsk_")
            and not col.endswith("_Group A")
            and not col.endswith("_Group B")
        )

    body_parts = [
        col.replace("Tsk_", "") for col in df_nude.columns if is_valid_body_part(col)
    ]

    def compute_icls(df_clothed, condition_label):
        results = []

        env_keys = ["Ta", "Tg", "Twb", "To", "MRT", "RH", "V"]
        env_values = {
            key: float(df_clothed[key].iloc[0])
            for key in env_keys
            if key in df_clothed.columns
        }
        # Get operative temperature in each condition
        try:
            t_o_nude = float(df_nude["To"].iloc[0])
            t_o_clothed = float(df_clothed["To"].iloc[0])
            print(
                f"[INFO] To values for {condition_label}: t_o_nude = {t_o_nude}, t_o_clothed = {t_o_clothed}"
            )
        except Exception as e:
            print(f"[Warning] Could not retrieve To values for {condition_label}: {e}")
            return pd.DataFrame([])

        for part in body_parts:
            try:

                def extract_single_value(df, key):
                    return float(df[key].iloc[0])

                tsk_nude = extract_single_value(df=df_nude, key=f"Tsk_{part}")
                tsk_clothed = extract_single_value(df=df_clothed, key=f"Tsk_{part}")
                p_nude = extract_single_value(df=df_nude, key=f"P_{part}")
                p_clothed = extract_single_value(df=df_clothed, key=f"P_{part}")

                dict_results = calc_intrinsic_clothing_insulation(
                    t_skin_clothed=tsk_clothed,
                    t_skin_nude=tsk_nude,
                    t_o_clothed=t_o_clothed,
                    t_o_nude=t_o_nude,
                    q_total_clothed=p_clothed,
                    q_total_nude=p_nude,
                )

                results.append(
                    {
                        "Clothing_ID": condition_label,
                        "BodyPart": part,
                        "Tsk_clothed": tsk_clothed,
                        "Tsk_nude": tsk_nude,
                        "P_clothed": p_clothed,
                        "P_nude": p_nude,
                        "It": dict_results["It"],
                        "Ia": dict_results["Ia"],
                        "Icl": dict_results["Icl"],
                        "fcl": dict_results["fcl"],
                        **env_values,
                    }
                )

            except Exception as e:
                print(f"[Warning] Skipped {part} in {condition_label}: {e}")
                continue

        return pd.DataFrame(results)

    df_summary_summer = compute_icls(df_summer, condition_label=1)
    df_summary_winter = compute_icls(df_winter, condition_label=2)

    df_all = pd.concat([df_summary_summer, df_summary_winter], ignore_index=True)
    df_all = utils.change_decimal_places(df=df_all, decimal_places=2)
    df_all.to_csv(
        path_or_buf=os.path.join(
            Config.DataPaths.PROCESSED_DATA_DIR, "clothing_measurement_data.csv"
        ),
        index=False,
    )
    print(df_all)

    # Preprocess the clothing data
    df_clothing_for_metadata = change_df_format_to_match_metadata(df=df_all)
    df_clothing_for_metadata.to_csv(
        os.path.join(Config.DataPaths.METADATA_DIR, "clothing_info.csv"),
        index=True,
    )


if __name__ == "__main__":
    main()
