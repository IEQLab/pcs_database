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

Schema Description (Generated on 2025-02-27 10:44:58)

| Parameter | Type | Description | Example |
|---|---|---|---|
| **`ID`** | *integer* | Unique identifier for each PCS. | 1 |
| **`Category`** | *string* | Category of the PCS. Must be one of: `Cooling, Heating`. | Cooling |
| **`Type`** | *string* | Type of PCS (e.g., fan, foot warmer). Must be one of: `Cooling, Heating`. | Small desk fan |
| **`Brand`** | *string* | Brand name of the PCS. | Simpeak |
| **`PCS_Reference`** | *string* | Reference URL of PCS. | Reference link |
| **`PCS_Intensity`** | *string* | Intensity level of the PCS. | Low |
| **`Price_USD`** | *number* | Price of the PCS in US dollars. | 10 |
| **`Angle`** | *number* | Angle of the PCS and target (degrees). | 125.0 |
| **`Distance`** | *number* | Distance from PCS to target (m). | 60.0 |
| **`Target_Body`** | *string* | Targeted body segment for PCS application. | Face |
| **`Power_W`** | *number* | Energy consumption of the PCS (W). | 2 |
| **`DateTime`** | *string* | Timestamp of data entry. | 2025-02-01T17:18:00Z |
| **`Place`** | *string* | Location where the measurement was taken. | The University of Sydney |
| **`Posture`** | *string* | Posture of the manikin during measurement (e.g., standing, sitting). | Sitting |
| **`Situation`** | *string* | Description of the environment where PCS is used (e.g., office, car). | Office |
| **`Manikin_Company`** | *string* | Manufacturer of the thermal manikin used. | PT Manikins |
| **`Manikin_Gender`** | *string* | Gender representation of the thermal manikin. Must be one of: `Male, Female`. | Female |
| **`Manikin_Body_Segments`** | *integer* | Number of body segments of the thermal manikin. | 22 |
| **`Control_Method`** | *string* | Method used to control the PCS (e.g., manual, automatic). Must be one of: `TskControl, HeatFluxControl, ComfortControl`. | TskControl34 |
| **`Ta`** | *number* | Ambient air temperature (°C). | 25 |
| **`MRT`** | *number* | Mean radiant temperature (°C). | 25 |
| **`RH`** | *number* | Relative humidity (%). | 50 |
| **`V`** | *number* | Air velocity (m/s). | 0.1 |
| **`Delta_Teq_`** | *object* | Equivalent temperature change for specific body parts. See #/definitions/BodyPart | N/A |
| **`Delta_P_`** | *object* | Change in perceived temperature or power supply for specific body parts. See #/definitions/BodyPart | N/A |
| **`Clo_`** | *object* | Clothing insulation value for specific body parts. See #/definitions/BodyPart | N/A |
| **`Image_Path`** | *string* | File path of related images. | N/A |

## Definitions
- **`BodyPart`** *(type: object)* - Properties: `Crown`, `Head`, `Left_Chest`, `Right_Chest`, `Left_Back`, `Right_Back`, `Abdomen`, `Buttocks`, `Left_Upper_Arm`, `Right_Upper_Arm`, `Left_Forearm`, `Right_Forearm`, `Left_Hand`, `Right_Hand`, `Left_Front_Thigh`, `Right_Front_Thigh`, `Left_Back_Thigh`, `Right_Back_Thigh`, `Left_Lower_Leg`, `Right_Lower_Leg`, `Left_Foot`, `Right_Foot`

<!-- METADATA_END -->

There is [an example PCS database](data/PCS_database_example.csv)
