from dataclasses import dataclass
from enum import Enum


# TODO: need to be checked carefully
class BodyPartLaura(Enum):
    CROWN = {"name": "Crown", "area": 0.049}
    HEAD = {"name": "Head", "area": 0.09}
    LEFT_CHEST = {"name": "Left Chest", "area": 0.07}
    RIGHT_CHEST = {"name": "Right Chest", "area": 0.07}
    LEFT_BACK = {"name": "Left Back", "area": 0.07}
    RIGHT_BACK = {"name": "Right Back", "area": 0.07}
    SIDE_BACK = {
        "name": "Side Back",
        "area": 0.11,
    }  # TODO need to be checked where exactly this part is located
    PELVIS = {"name": "Pelvis", "area": 0.055}
    LEFT_UPPER_ARM = {"name": "Left Upper Arm", "area": 0.074}
    RIGHT_UPPER_ARM = {"name": "Right Upper Arm", "area": 0.076}
    LEFT_FOREARM = {"name": "Left Forearm", "area": 0.05}
    RIGHT_FOREARM = {"name": "Right Forearm", "area": 0.05}
    LEFT_HAND = {"name": "Left Hand", "area": 0.038}
    RIGHT_HAND = {"name": "Right Hand", "area": 0.038}
    LEFT_FRONT_THIGH = {"name": "Left Front Thigh", "area": 0.09}
    RIGHT_FRONT_THIGH = {"name": "Right Front Thigh", "area": 0.09}
    LEFT_BACK_THIGH = {"name": "Left Back Thigh", "area": 0.09}
    RIGHT_BACK_THIGH = {"name": "Right Back Thigh", "area": 0.09}
    LEFT_LOWER_LEG = {"name": "Left Lower Leg", "area": 0.0975}
    RIGHT_LOWER_LEG = {"name": "Right Lower Leg", "area": 0.0975}
    LEFT_FOOT = {"name": "Left Foot", "area": 0.048}
    RIGHT_FOOT = {"name": "Right Foot", "area": 0.048}

    # Get the name of the body part
    @property
    def name(self):
        return self.value["name"]

    # Get the area of the body part
    @property
    def area(self):
        return self.value["area"]


# Example usage
if __name__ == "__main__":
    # Print all body parts with their names and areas
    for part in BodyPartLaura:
        print(f"Body Part: {part.name}, Area: {part.area}m2")

    # Access specific body parts
    print("\nSpecific Parts:")
    print(f"{BodyPartLaura.CROWN.name} has an area of {BodyPartLaura.CROWN.area}m2")
    # print(f"{BodyPart.BUTTOCKS.name} has an area of {BodyPart.BUTTOCKS.area}㎡")

    # Calculate and print the total area
    total_area = sum(part.area for part in BodyPartLaura)
    number_of_body_area = len(BodyPartLaura)
    print(f"\nNumber of Surface Area: {number_of_body_area}")
    print(f"\nTotal Surface Area: {total_area}m2")


# @dataclass
# class BodyPart:
#     Crown: str = "Crown"
#     Head: str = "Head"
#     Left_Chest: str = "Left Chest"
#     Right_Chest: str = "Right Chest"
#     Left_Back: str = "Left Back"
#     Right_Back: str = "Right Back"
#     Abdomen: str = "Abdomen"
#     Buttocks: str = "Buttocks"
#     Left_Upper_Arm: str = "Left Upper Arm"
#     Right_Upper_Arm: str = "Right Upper Arm"
#     Left_Forearm: str = "Left Forearm"
#     Right_Forearm: str = "Right Forearm"
#     Left_Hand: str = "Left Hand"
#     Right_Hand: str = "Right Hand"
#     Left_Front_Thigh: str = "Left Front Thigh"
#     Right_Front_Thigh: str = "Right Front Thigh"
#     Left_Back_Thigh: str = "Left Back Thigh"
#     Right_Back_Thigh: str = "Right Back Thigh"
#     Left_Lower_Leg: str = "Left Lower Leg"
#     Right_Lower_Leg: str = "Right Lower Leg"
#     Left_Foot: str = "Left Foot"
#     Right_Foot: str = "Right Foot"
#
# if __name__ == "__main__":
#     # Example: Accessing body parts
#     manikin = BodyPart()
#     print(manikin.Crown)  # Output: Crown
#     print(manikin.Left_Hand)  # Output: Left Hand
