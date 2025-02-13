import os
import numpy as np
import pandas as pd
import chardet
from datetime import timedelta
import re
from collections import defaultdict
import configuration as config
from pythermalcomfort.utilities import mean_radiant_tmp

# Load the CSV file
test_file_path = os.path.join(config.CHAMBER_DATA_DIR, "2025-02-11_Chamber_Thermal_Environment.csv")
df = pd.read_csv(test_file_path, header=None)

# Set the 11th row as column names
df.columns = df.iloc[11]
df_new = df[12:].reset_index(drop=True)

# # Convert all columns (except index) to numeric
# df_new = df_new.apply(pd.to_numeric, errors="coerce")

# Select necessary columns
selected_columns = ["Session name:", "Time:", "Temperature", "Relative Humidity", "WBGT", "Air Velocity", "Effective Temperature"]
df_selected = df_new[selected_columns].copy()

# Create "Datetime" column by combining "Session name:" and "Time:" and convert to datetime type
df_selected["Datetime"] = df_selected["Session name:"].astype(str) + " " + df_selected["Time:"].astype(str)
df_selected["Datetime"] = pd.to_datetime(df_selected["Datetime"], errors='coerce')

# Set "Datetime" as index and remove unnecessary columns
df_selected = df_selected.set_index("Datetime").drop(columns=["Session name:", "Time:"])

# Convert all columns (except index) to numeric
df_selected = df_selected.apply(pd.to_numeric, errors="coerce")

# Find and rename WBGT columns
df_wbgt_columns = [i for i, col in enumerate(df_selected.columns) if "WBGT" in str(col)]
df_temperature_columns = [i for i, col in enumerate(df_selected.columns) if "Temperature" in str(col)]

if len(df_wbgt_columns) >= 4:
    df_selected.columns.values[df_wbgt_columns[0]] = "Twb"
    df_selected.columns.values[df_wbgt_columns[1]] = "Tg"
    df_selected.columns.values[df_wbgt_columns[2]] = "Ta"
    df_selected.columns.values[df_wbgt_columns[3]] = "WBGT"
    df_selected = df_selected.drop(columns=["Ta"], errors='ignore')

if len(df_temperature_columns) >= 2:
    df_selected.columns.values[df_temperature_columns[0]] = "Ta"
    df_selected.columns.values[df_temperature_columns[1]] = "To"
    df_selected = df_selected.drop(columns=["To"], errors='ignore')

# Rename the specified columns
rename_dict = {
    "Relative Humidity": "RH",
    "Air Velocity": "V",
    "Effective Temperature": "ET"
}
df_selected = df_selected.rename(columns=rename_dict)

# Calculate Mean Radiant Temperature (MRT) using pythermalcomfort
df_selected["MRT"] = df_selected.apply(lambda row: mean_radiant_tmp(
    tg=row["Tg"], tdb=row["Ta"], v=row["V"], d=0.15, emissivity=0.95, standard="ISO"), axis=1)

# Reorder the columns for better readability
order = ["Ta", "Tg", "Twb", "MRT", "RH", "V", "WBGT", "ET"]
df_selected = df_selected[order]

# Save processed data
df_selected.to_csv(os.path.join(config.PROCESSED_DATA_DIR, "chamber_thermal_environment.csv"))



# import os
# import numpy as np
# import pandas as pd
# import chardet
# from datetime import timedelta
# import re
# from collections import defaultdict
# import configuration as config
# from pythermalcomfort.utilities import mean_radiant_tmp
#
#
# test_file_path = os.path.join(config.CHAMBER_DATA_DIR, "2025-02-11_Chamber_Thermal_Environment.csv")
# print(test_file_path)
#
# df = pd.read_csv(test_file_path, header=None)
#
# # Set the 11th row as column names
# df.columns = df.iloc[11]
# df_new = df[12:].reset_index(drop=True)
#
#
#
# # Select necessary columns
# selected_columns = ["Session name:", "Time:", "Temperature", "Relative Humidity", "WBGT", "Air Velocity",
#                     "Effective Temperature"]
# df_selected = df_new[selected_columns].copy()
#
# # Create "Datetime" column by combining "Session name:" and "Time:" and convert to datetime type
# df_selected["Datetime"] = df_selected["Session name:"].astype(str) + " " + df_selected["Time:"].astype(str)
# df_selected["Datetime"] = pd.to_datetime(df_selected["Datetime"], errors='coerce')
#
# # Set "Datetime" as index and remove unnecessary columns
# df_selected = df_selected.set_index("Datetime").drop(columns=["Session name:", "Time:"])
# print(df_selected.columns)
#
# # Convert all columns (except index) to numeric
# for col in df_selected.select_dtypes(include=['object']).columns:
#     df_selected[col] = pd.to_numeric(df_selected[col], errors="coerce")
#
# # Find columns containing "WBG
# # T" and rename them
# df_wbgt_columns = [i for i, col in enumerate(df_selected.columns) if "WBGT" in str(col)]
# df_temperature_columns = [i for i, col in enumerate(df_selected.columns) if "Temperature" in str(col)]
#
# # If there are at least 3 WBGT columns, rename them correctly
# if len(df_wbgt_columns) >= 4:
#     # Rename the four WBGT columns explicitly
#     df_selected.columns.values[df_wbgt_columns[0]] = "Twb"
#     df_selected.columns.values[df_wbgt_columns[1]] = "Tg"
#     df_selected.columns.values[df_wbgt_columns[2]] = "Ta"
#     df_selected.columns.values[df_wbgt_columns[3]] = "WBGT"
#
#     if "Ta" in df_selected.columns:
#         df_selected = df_selected.drop(columns=["Ta"])
#
# if len(df_temperature_columns)>=2:
#     df_selected.columns.values[df_temperature_columns[0]] = "Ta"
#     df_selected.columns.values[df_temperature_columns[1]] = "To"
#
#     # Drop 'To' column if it exists
#     if "To" in df_selected.columns:
#         df_selected = df_selected.drop(columns=["To"])
#
# # Rename the specified columns
# rename_dict = {
#     "Relative Humidity": "RH",
#     "Air Velocity": "V",
#     "Effective Temperature": "ET"
# }
#
# df_selected = df_selected.rename(columns=rename_dict)
#
# # Calculate Mean Radiant Temperature (MRT) using pythermalcomfort
# # https://pythermalcomfort.readthedocs.io/en/latest/documentation/utilities_functions.html#mean-radiant-temperature
# # Assuming emissivity (ε) of the globe thermometer is 0.95.
# # Diameter of the globe thermometer was 0.15 m
# df_selected["MRT"] = df_selected.apply(lambda row: mean_radiant_tmp(tg=row["Tg"], tdb=row["Ta"], v=row["V"], d=0.15, emissivity=0.95, standard="ISO"), axis=1)
#
# # Reorder the columns for better readability
# order = ["Ta", "Tg", "Twb", "RH", "V", "WBGT", "ET"]
# df_selected = df_selected[order]
#
# df_selected.to_csv(os.path.join(config.PROCESSED_DATA_DIR, "chamber_thermal_environment.csv"))
# print(df_selected)