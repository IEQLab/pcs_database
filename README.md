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
| Key | Value | Example |
|---|---|---|
| - **`columns`** *(object)* | Metadata for each column in the PCS database CSV. |  |
| - **`ID`** *(integer)* | Unique identifier for each PCS. |  |
| - **`Category`** *(string)* | Category of the PCS. Must be one of: `["Cooling", "Heating"]`. |  |
| - **`Type`** *(string)* | Type of PCS (e.g., fan, foot warmer). |  |
| - **`Brand`** *(string)* | Brand name of the PCS. |  |
| - **`PCS_Reference`** *(string)* | Reference URL of PCS. |  |
| - **`PCS_Intensity`** *(string)* | Intensity level of the PCS. |  |
| - **`Price_USD`** *(number)* | Price of the PCS in US dollars. |  |
| - **`Angle`** *(number)* | Angle of the PCS air or radiation (degrees). |  |
| - **`Distance`** *(number)* | Distance from PCS to target (m). |  |
| - **`Target_Body`** *(string)* | Targeted body region for PCS application. |  |
| - **`Power_W`** *(number)* | Power consumption of the PCS (W). |  |
| - **`DateTime`** *(string, format | date-time)*: Timestamp of data entry. |  |
| - **`Place`** *(string)* | Location where the measurement was taken. |  |
| - **`Posture`** *(string)* | Posture of the manikin during measurement (e.g., standing, sitting). |  |
| - **`Situation`** *(string)* | Description of the environment where PCS is used (e.g., office, car). |  |
| - **`Manikin_Company`** *(string)* | Manufacturer of the thermal manikin used. |  |
| - **`Manikin_Gender`** *(string)* | Gender representation of the thermal manikin. Must be one of: `["Male", "Female"]`. |  |
| - **`Manikin_Body_Segments`** *(integer)* | Number of body segments modeled in the thermal manikin. |  |
| - **`Control_Method`** *(string)* | Method used to control the PCS (e.g., manual, automatic). |  |
| - **`Ta`** *(number)* | Ambient air temperature (ﾂｰC). |  |
| - **`MRT`** *(number)* | Mean radiant temperature (ﾂｰC). |  |
| - **`RH`** *(number)* | Relative humidity (%). |  |
| - **`V`** *(number)* | Air velocity (m/s). |  |

**Definitions:**
Examples:
```json
{
"Crown": -1.5,
"Head": -1.0,
"Left_Chest": -0.8,
"Right_Chest": -0.8,
"OTHER BODY PARTS": -0.8
}
```
- **`Image_Path`** *(string)*: File path of related images.
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
<!-- METADATA_END -->
