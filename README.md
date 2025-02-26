# PCS Database

This repository is for a database of PCS (Personal Comfort System) such as a desk fan and foot warmer. 
Each PCS cooling/heating effects on the human body was quantified using a thermal manikin in a climate controlled chamber
at the IEQLab of The University of Sydney.

The repository contains the data and the related code to generate database as the following file structure.
Please note that all the image files are not stored in this repository due to the limited storage of this repository,
but you can access them at [here](https://unisyd-my.sharepoint.com/:f:/r/personal/akihisa_nomoto_sydney_edu_au/Documents/PCS%20Database?csf=1&web=1&e=QgKj7a) upon request.

We also offer a simple web application for this database, which you can access at https://pcs-database.onrender.com. 
(Please note that we may change the hosting service in the future.)

Each time you start using our service, it may take up to a minute to wake up—just like a sleeping koala 🐨🐨🐨. 
This is a characteristic of the free hosting service we currently use, which puts applications to sleep when there is no traffic.

    
    ```
    ├── code # Python code to generate the database
    ├── data
        ├── raw_data # Output results from the thermal manikin
        ├── processed_data # Processed data by the code
        ├── PCS_Database.csv # Database
        └── metadata.json # For detailed descriptions
    ├── figure # For generated figures
    ├── image # For images of experiment/each PCS
    ├── manuscript
    ├── presentation
    ├── reference
    └── out
    ``



<!-- METADATA_START -->
# Database Metadata

Schema Description (Generated on 2025-02-26 19:40:36)

| Parameter | Description |
|---|---|
| - **`ID`** | Unique identifier for each PCS. |
| - **`Category`** | Category of the PCS. |
| - **`Type`** | Type of PCS (e.g., fan, foot warmer). |
| - **`Brand`** | Brand name of the PCS. |
| - **`PCS_Reference`** | Reference URL of PCS. |
| - **`PCS_Intensity`** | Intensity level of the PCS. |
| - **`Price_USD`** | Price of the PCS in US dollars. |
| - **`Angle`** | Angle of the PCS air or radiation (degrees). |
| - **`Distance`** | Distance from PCS to target (m). |
| - **`Target_Body`** | Targeted body region for PCS application. |
| - **`Power_W`** | Power consumption of the PCS (W). |
| - **`DateTime`** | Timestamp of data entry. |
| - **`Place`** | Location where the measurement was taken. |
| - **`Posture`** | Posture of the manikin during measurement (e.g., standing, sitting). |
| - **`Situation`** | Description of the environment where PCS is used (e.g., office, car). |
| - **`Manikin_Company`** | Manufacturer of the thermal manikin used. |
| - **`Manikin_Gender`** | Gender representation of the thermal manikin. |
| - **`Manikin_Body_Segments`** | Number of body segments modeled in the thermal manikin. |
| - **`Control_Method`** | Method used to control the PCS (e.g., manual, automatic). |
| - **`Ta`** | Ambient air temperature (°C). |
| - **`MRT`** | Mean radiant temperature (°C). |
| - **`RH`** | Relative humidity (%). |
| - **`V`** | Air velocity (m/s). |
| - **`Delta_Teq`** | Equivalent temperature change for specific body parts. |
| - **`Delta_P`** | Change in perceived temperature or power supply for specific body parts. |
| - **`Clo`** | Clothing insulation value for specific body parts. |
| - **`Image_Path`** | File path of related images. |

## Definitions

- <a id="definitions/BodyPart"></a>**`BodyPart`** *(object)*: Body parts affected by PCS.
  - **`Crown`** *(number)*
  - **`Head`** *(number)*
  - **`Left_Chest`** *(number)*
  - **`Right_Chest`** *(number)*
  - **`Left_Back`** *(number)*
  - **`Right_Back`** *(number)*
  - **`Abdomen`** *(number)*
  - **`Buttocks`** *(number)*
  - **`Left_Upper_Arm`** *(number)*
  - **`Right_Upper_Arm`** *(number)*
  - **`Left_Forearm`** *(number)*
  - **`Right_Forearm`** *(number)*
  - **`Left_Hand`** *(number)*
  - **`Right_Hand`** *(number)*
  - **`Left_Front_Thigh`** *(number)*
  - **`Right_Front_Thigh`** *(number)*
  - **`Left_Back_Thigh`** *(number)*
  - **`Right_Back_Thigh`** *(number)*
  - **`Left_Lower_Leg`** *(number)*
  - **`Right_Lower_Leg`** *(number)*
  - **`Left_Foot`** *(number)*
  - **`Right_Foot`** *(number)*

<!-- METADATA_END -->
