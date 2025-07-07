import os
import pandas as pd
from config.configuration import Config
from preprocess_manikin import average_last_five_minute, reorder_columns, match_nearest_datetime
import preprocess_chamber
from calc_clothing_insulation import calc_intrinsic_clothing_insulation

# Config
columns_format_file = os.path.join(Config.DataPaths.DATA_DIR, "columns_format.csv")
columns_format = pd.read_csv(columns_format_file).columns.tolist()

df_chamber = preprocess_chamber.main()

# File paths
nude_file_path = os.path.join(Config.DataPaths.CLOTHING_DATA_DIR,
    "2025-05-09_ClothingMeasurement_Ta21_TskControl34_Nude.csv")
summer_clothing_file_path = os.path.join(Config.DataPaths.CLOTHING_DATA_DIR,
    "2025-05-09_ClothingMeasurement_Ta21_TskControl34_SummerClothing.csv")
winter_clothing_file_path = os.path.join(Config.DataPaths.CLOTHING_DATA_DIR,
    "2025-05-08_ClothingMeasurement_Ta21_TskControl34_WinterClothing.csv")

# Dataframes
def load_and_process_data(file_path, columns_format):
    """Average the data for the last 5 min and reorder the columns"""
    df = average_last_five_minute(file_path, columns_format)
    return reorder_columns(df)

df_nude = load_and_process_data(file_path=nude_file_path, columns_format=columns_format)
df_summer = load_and_process_data(file_path=summer_clothing_file_path, columns_format=columns_format)
df_winter = load_and_process_data(file_path=winter_clothing_file_path, columns_format=columns_format)
# df_nude = match_nearest_datetime(df_nude, df_chamber)

def main():
    t_o_fixed = 21.0
    body_parts = [col.replace("Tsk_", "") for col in df_nude.columns if col.startswith("Tsk_") and not col.endswith("_All")]

    icl_results = []

    for part in body_parts:
        try:
            def extract_single_value(df, key):
                """Extract the first value from a column and convert it to float."""
                return float(df[key].iloc[0])

            tsk_nude = extract_single_value(df=df_nude, key=f"Tsk_{part}")
            tsk_clothed = extract_single_value(df=df_summer, key=f"Tsk_{part}")
            p_nude = extract_single_value(df=df_nude, key=f"P_{part}")
            p_clothed = extract_single_value(df=df_summer, key=f"P_{part}")

            # Calculate Icl (fixed To for now)
            dict_results = calc_intrinsic_clothing_insulation(
                t_skin_clothed=tsk_clothed,
                t_skin_nude=tsk_nude,
                t_o_clothed=t_o_fixed,
                t_o_nude=t_o_fixed,
                q_total_clothed=p_clothed,
                q_total_nude=p_nude
            )

            icl_results.append({
                "BodyPart": part,
                "Tsk_clothed": tsk_clothed,
                "Tsk_nude": tsk_nude,
                "P_clothed": p_clothed,
                "P_nude": p_nude,
                "It": dict_results["It"],
                "Ia": dict_results["Ia"],
                "Icl": dict_results["Icl"],
                "fcl": dict_results["fcl"]
            })

        except Exception as e:
            print(f"[Warning] Skipped {part}: {e}")
            continue

    df_summary = pd.DataFrame(icl_results)

    df_summary.to_csv("clothing_measurement_data.csv", index=False)
    print(df_summary)

if __name__ == "__main__":
    main()
