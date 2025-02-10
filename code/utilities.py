import pandas as pd
from dataclasses import dataclass

@dataclass
class BodyPart:
    Crown: str = "Crown"
    Head: str = "Head"
    Left_Chest: str = "Left Chest"
    Right_Chest: str = "Right Chest"
    Left_Back: str = "Left Back"
    Right_Back: str = "Right Back"
    Abdomen: str = "Abdomen"
    Buttocks: str = "Buttocks"
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

@dataclass
# This is for manikin's output data format
class BodyPartTemporary:
    # Lower Body
    Left_Foot: str = "Left Foot"
    Right_Foot: str = "Right Foot"
    Left_Lower_Leg: str = "Left Lower Leg"
    Right_Lower_Leg: str = "Right Lower Leg"
    Left_Front_Thigh: str = "Left Front Thigh"
    Right_Front_Thigh: str = "Right Front Thigh"
    Left_Back_Thigh: str = "Left Back Thigh"
    Right_Back_Thigh: str = "Right Back Thigh"
    Buttocks: str = "Buttocks"
    Abdomen: str = "Abdomen"
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

