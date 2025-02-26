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

Schema Description (Generated on 2025-02-27 10:08:57)

| Parameter | Type | Enum | Description |
|---|---|---|---|
| - **`ID`** | integer | N/A | Unique identifier for each PCS. |
| - **`Category`** | string | Cooling, Heating | Category of the PCS. |
| - **`Type`** | string | Cooling, Heating | Type of PCS (e.g., fan, foot warmer). |
| - **`Brand`** | string | N/A | Brand name of the PCS. |
| - **`PCS_Reference`** | string | N/A | Reference URL of PCS. |
| - **`PCS_Intensity`** | string | N/A | Intensity level of the PCS. |
| - **`Price_USD`** | number | N/A | Price of the PCS in US dollars. |
| - **`Angle`** | number | N/A | Angle of the PCS and target (degrees). |
| - **`Distance`** | number | N/A | Distance from PCS to target (m). |
| - **`Target_Body`** | string | N/A | Targeted body segment for PCS application. |
| - **`Power_W`** | number | N/A | Energy consumption of the PCS (W). |
| - **`DateTime`** | string | N/A | Timestamp of data entry. |
| - **`Place`** | string | N/A | Location where the measurement was taken. |
| - **`Posture`** | string | N/A | Posture of the manikin during measurement (e.g., standing, sitting). |
| - **`Situation`** | string | N/A | Description of the environment where PCS is used (e.g., office, car). |
| - **`Manikin_Company`** | string | N/A | Manufacturer of the thermal manikin used. |
| - **`Manikin_Gender`** | string | Male, Female | Gender representation of the thermal manikin. |
| - **`Manikin_Body_Segments`** | integer | N/A | Number of body segments of the thermal manikin. |
| - **`Control_Method`** | string | TskControl, HeatFluxControl, ComfortControl | Method used to control the PCS (e.g., manual, automatic). |
| - **`Ta`** | number | N/A | Ambient air temperature (°C). |
| - **`MRT`** | number | N/A | Mean radiant temperature (°C). |
| - **`RH`** | number | N/A | Relative humidity (%). |
| - **`V`** | number | N/A | Air velocity (m/s). |
| - **`Delta_Teq_`** | object | N/A | Equivalent temperature change for specific body parts. |
| - **`Delta_P_`** | object | N/A | Change in perceived temperature or power supply for specific body parts. |
| - **`Clo_`** | object | N/A | Clothing insulation value for specific body parts. |
| - **`Image_Path`** | string | N/A | File path of related images. |

## Definitions

- <a id="definitions/BodyPart"></a>**`BodyPart`** *(type: object)*: Body parts affected by PCS.
  - **Enum**: N/A
  - **`Crown`** *(type: number, enum: N/A)*
  - **`Head`** *(type: number, enum: N/A)*
  - **`Left_Chest`** *(type: number, enum: N/A)*
  - **`Right_Chest`** *(type: number, enum: N/A)*
  - **`Left_Back`** *(type: number, enum: N/A)*
  - **`Right_Back`** *(type: number, enum: N/A)*
  - **`Abdomen`** *(type: number, enum: N/A)*
  - **`Buttocks`** *(type: number, enum: N/A)*
  - **`Left_Upper_Arm`** *(type: number, enum: N/A)*
  - **`Right_Upper_Arm`** *(type: number, enum: N/A)*
  - **`Left_Forearm`** *(type: number, enum: N/A)*
  - **`Right_Forearm`** *(type: number, enum: N/A)*
  - **`Left_Hand`** *(type: number, enum: N/A)*
  - **`Right_Hand`** *(type: number, enum: N/A)*
  - **`Left_Front_Thigh`** *(type: number, enum: N/A)*
  - **`Right_Front_Thigh`** *(type: number, enum: N/A)*
  - **`Left_Back_Thigh`** *(type: number, enum: N/A)*
  - **`Right_Back_Thigh`** *(type: number, enum: N/A)*
  - **`Left_Lower_Leg`** *(type: number, enum: N/A)*
  - **`Right_Lower_Leg`** *(type: number, enum: N/A)*
  - **`Left_Foot`** *(type: number, enum: N/A)*
  - **`Right_Foot`** *(type: number, enum: N/A)*

<!-- METADATA_END -->

There is [an example PCS database](data/PCS_database_example.csv)
