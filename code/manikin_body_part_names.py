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

if __name__ == "__main__":
    # Example: Accessing body parts
    manikin = BodyPart()
    print(manikin.Crown)  # Output: Crown
    print(manikin.Left_Hand)  # Output: Left Hand
