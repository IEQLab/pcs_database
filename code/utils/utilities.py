import pandas as pd
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
