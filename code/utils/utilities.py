import pandas as pd
import numpy as np
from dataclasses import dataclass


def weighted_average(values, weights):
    return sum(v * w for v, w in zip(values, weights)) / sum(weights)


def filter_by_target_temperature(df: pd.DataFrame, target_ta: float = 25.0, tolerance: float = 1.0, 
                                ta_column: str = 'PCS_Ta') -> pd.DataFrame:
    """
    Filter DataFrame by target ambient temperature ± tolerance.
    
    Args:
        df: Input DataFrame containing temperature data
        target_ta: Target ambient temperature in °C (default: 25.0)
        tolerance: Temperature tolerance in °C (default: 1.0)
        ta_column: Column name containing ambient temperature data (default: 'PCS_Ta')
    
    Returns:
        Filtered DataFrame containing only records within target_ta ± tolerance
    
    Example:
        # Filter for 25°C ± 1°C (24-26°C range)
        filtered_df = filter_by_target_temperature(df, target_ta=25.0, tolerance=1.0)
    """
    if ta_column not in df.columns:
        raise ValueError(f"Column '{ta_column}' not found in DataFrame")
    
    min_ta = target_ta - tolerance
    max_ta = target_ta + tolerance
    
    filtered_df = df[(df[ta_column] >= min_ta) & (df[ta_column] <= max_ta)].copy()
    
    print(f"Temperature filtering: {target_ta}°C ± {tolerance}°C ({min_ta}-{max_ta}°C range)")
    print(f"Records before filtering: {len(df)}")
    print(f"Records after filtering: {len(filtered_df)}")
    
    return filtered_df


def compute_mid_level_effect(df_device: pd.DataFrame, value_column: str = 'Delta_Teq_All') -> dict:
    """
    Compute mid-level effect from numeric PCS_Level data.
    
    This function implements the mid-level calculation logic:
    - For each PCS_Level, compute the median of the value_column
    - Mid effect calculation:
        - If odd number of levels: use median at middle level
        - If even number of levels: average of medians at two middle levels
    
    Args:
        df_device: DataFrame containing PCS_Level and value data for one device
        value_column: Column name containing the values to compute (default: 'Delta_Teq_All')
    
    Returns:
        Dictionary with keys: median, min, max, used_levels, n_levels, show_range, point_level
        Returns empty dict if no valid data found
    
    Example:
        # Get mid-level effect for a specific PCS device
        device_data = df[df['PCS_ID'] == 8]
        mid_stats = compute_mid_level_effect(device_data, 'Delta_Teq_All')
    """
    # Keep only needed columns
    df = df_device[["PCS_Level", value_column]].dropna(subset=["PCS_Level", value_column]).copy()
    if df.empty:
        return {}

    # Group by numeric level and compute per-level medians; sort by level value
    level_medians = df.groupby("PCS_Level")[value_column].median().sort_index()
    if level_medians.empty:
        return {}

    levels = level_medians.index.to_list()
    L = len(levels)

    show_range = True
    point_level = None

    if L == 1:
        # Single level: plot point only, no range
        mid_effect = float(level_medians.iloc[0])
        show_range = False
        point_level = float(levels[0])
    elif L == 2:
        # Two levels: use the smaller effect as point, show range to larger effect
        low_med = float(level_medians.iloc[0])
        high_med = float(level_medians.iloc[1])
        if low_med <= high_med:
            # Normal case: Level 0 ≤ Level 1
            mid_effect = low_med
            point_level = float(levels[0])
        else:
            # Inverted case: Level 0 > Level 1 (e.g., ID20)
            mid_effect = high_med
            point_level = float(levels[1])
    else:
        # 3+ levels: standard mid logic
        if L % 2 == 1:
            mid_effect = float(level_medians.iloc[L // 2])
            point_level = float(levels[L // 2])
        else:
            mid_effect = float((level_medians.iloc[L // 2 - 1] + level_medians.iloc[L // 2]) / 2.0)
            point_level = float((levels[L // 2 - 1] + levels[L // 2]) / 2.0)

    return {
        "median": float(mid_effect),
        "min": float(level_medians.min()),
        "max": float(level_medians.max()),
        "used_levels": levels,
        "n_levels": L,
        "show_range": show_range,
        "point_level": point_level,
        "level_medians": level_medians
    }


# Capoitalize the first letter of each word with underscores replaced by spaces
def capitalize_first_letter_with_underscores(string):
    """Capitalize the first letter of each word in a string with underscores replaced by spaces"""
    return " ".join(word.capitalize() for word in string.replace("_", " ").split())


def replace_space_to_underscore(string):
    """Change spaces in a string to underscores"""
    return string.replace(" ", "_")


# Change disimal nummers to 2 decimal places in numerical coloums in a DataFrame
def change_decimal_places(df: pd.DataFrame, decimal_places: int = 2) -> pd.DataFrame:
    """Change decimal places of numerical columns in a DataFrame"""
    for col in df.select_dtypes(include=["float64", "int64"]).columns:
        df[col] = df[col].round(decimal_places)
    return df


@dataclass
class BodyPart:
    Crown: str = "Crown"
    Head: str = "Head"
    Left_Chest: str = "Left Chest"
    Right_Chest: str = "Right Chest"
    Left_Back: str = "Left Back"
    Right_Back: str = "Right Back"
    Back_side: str = "Back Side"
    Pelvis: str = "Pelvis"
    Left_Upper_Arm: str = "Left Upper Arm"
    Right_Upper_Arm: str = "Right Upper Arm"
    Left_Forearm: str = "Left Forearm"
    Right_Forearm: str = "Right Forearm"
    Left_Hand: str = "Left Hand"
    Right_Hand: str = "Right Hand"
    Left_Front_Thigh: str = "Left Front Thigh"
    Right_Front_Thigh: str = "Right Front Thigh"
    Left_Back_Thigh: str = "Left Back Thigh"
    Right_Back_Thigh: str = "Right Back Thigh"
    Left_Lower_Leg: str = "Left Lower Leg"
    Right_Lower_Leg: str = "Right Lower Leg"
    Left_Foot: str = "Left Foot"
    Right_Foot: str = "Right Foot"


rename_map = {
    "All": "All",
    "Group A": "Group A",
    "Group B": "Group B",
    "L. foot": "Left Foot",
    "R. foot": "Right Foot",
    "L. foreleg": "Left Foreleg",
    "R. foreleg": "Right Foreleg",
    "L. front thigh": "Left Front Thigh",
    "R. front thigh": "Right Front Thigh",
    "L. Back thigh": "Left Back Thigh",
    "R. Back thigh": "Right Back Thigh",
    "Pelvis": "Pelvis",
    "Back side": "Back Side",
    "Head": "Head",
    "Crown": "Crown",
    "L. Hand": "Left Hand",
    "R. Hand": "Right Hand",
    "L. Forearm": "Left Forearm",
    "R. Forearm": "Right Forearm",
    "L. Upper arm": "Left Upper Arm",
    "R. Upper arm": "Right Upper Arm",
    "Chest Left": "Chest Left",
    "Chest Right": "Chest Right",
    "Back Left": "Back Left",
    "Back Right": "Back Right",
    "Stability": "Stability",
}


# Todo: [IMPORTANT] Organize the dataclass for the manikin body parts
@dataclass
# This is for manikin's output data format
class BodyPartLauraOutput:
    # Lower Body
    Left_Foot: str = "Left Foot"
    Right_Foot: str = "Right Foot"
    Left_Lower_Leg: str = "Left Lower Leg"
    Right_Lower_Leg: str = "Right Lower Leg"
    Left_Front_Thigh: str = "Left Front Thigh"
    Right_Front_Thigh: str = "Right Front Thigh"
    Left_Back_Thigh: str = "Left Back Thigh"
    Right_Back_Thigh: str = "Right Back Thigh"
    Pelvis: str = "Pelvis"
    Back_Side: str = "Back Side"
    Head: str = "Head"
    Crown: str = "Crown"
    Left_Hand: str = "Left Hand"
    Right_Hand: str = "Right Hand"
    Left_Forearm: str = "Left Forearm"
    Right_Forearm: str = "Right Forearm"
    Left_Upper_Arm: str = "Left Upper Arm"
    Right_Upper_Arm: str = "Right Upper Arm"
    Left_Chest: str = "Left Chest"
    Right_Chest: str = "Right Chest"
    Left_Back: str = "Left Back"
    Right_Back: str = "Right Back"


@dataclass
class BodyPartDatabaseFormat:
    Head: str = "Head"
    Chest: str = "Chest"
    Back: str = "Back"
    Pelvis: str = "Pelvis"
    Left_Upper_Arm: str = "Left Upper Arm"
    Right_Upper_Arm: str = "Right Upper Arm"
    Left_Forearm: str = "Left Forearm"
    Right_Forearm: str = "Right Forearm"
    Left_Hand: str = "Left Hand"
    Right_Hand: str = "Right Hand"
    Left_Thigh: str = "Left Thigh"
    Right_Thigh: str = "Right Thigh"
    Left_Lower_Leg: str = "Left Lower Leg"
    Right_Lower_Leg: str = "Right Lower Leg"
    Left_Foot: str = "Left Foot"
    Right_Foot: str = "Right Foot"


# Define condition pairs and calculate deltas
# condition_pairs = [
#     ("withoutPCS_Ta25", "Daison_Fan_Level2_Ta25"),
#     ("withoutPCS_Ta25", "Daison_Fan_Level4_Ta25"),
#     ("withoutPCS_Ta25", "Daison_Fan_Level6_Ta25"),
#     ("withoutPCS_Ta25", "Neck_Fan_Level1_Ta25"),
#     ("withoutPCS_Ta25", "Neck_Fan_Level3_Ta25"),
#     ("withoutPCS_Ta25", "Neck_Fan_Level4_Ta25"),
# ]
# condition_pairs = [
#     ("2025-02-01_ID0_NoPCS", "2025-02-01_ID1_Small desk fan (grey)_Low"),
#     ("2025-02-01_ID0_NoPCS", "2025-02-01_ID1_Small desk fan (grey)_Mid"),
#     ("2025-02-01_ID0_NoPCS", "2025-02-01_ID1_Small desk fan (grey)_High"),
# ]
