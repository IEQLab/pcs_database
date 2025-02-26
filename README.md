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
| Key | Value |
|---|---|
| *Generated on 2025-02-26 19 | 49 |
| - **`columns`** *(object)* | Metadata for each column in the PCS database CSV. |
| - **`ID`** *(integer)* | Unique identifier for each PCS. |
| - **`Category`** *(string)* | Category of the PCS. Must be one of |
| - **`Type`** *(string)* | Type of PCS (e.g., fan, foot warmer). |
| - **`Brand`** *(string)* | Brand name of the PCS. |
| - **`PCS_Reference`** *(string)* | Reference URL of PCS. |
| - **`PCS_Intensity`** *(string)* | Intensity level of the PCS. |
| - **`Price_USD`** *(number)* | Price of the PCS in US dollars. |
| - **`Angle`** *(number)* | Angle of the PCS air or radiation (degrees). |
| - **`Distance`** *(number)* | Distance from PCS to target (m). |
| - **`Target_Body`** *(string)* | Targeted body region for PCS application. |
| - **`Power_W`** *(number)* | Power consumption of the PCS (W). |
| - **`DateTime`** *(string, format | date-time)* |
| - **`Place`** *(string)* | Location where the measurement was taken. |
| - **`Posture`** *(string)* | Posture of the manikin during measurement (e.g., standing, sitting). |
| - **`Situation`** *(string)* | Description of the environment where PCS is used (e.g., office, car). |
| - **`Manikin_Company`** *(string)* | Manufacturer of the thermal manikin used. |
| - **`Manikin_Gender`** *(string)* | Gender representation of the thermal manikin. Must be one of |
| - **`Manikin_Body_Segments`** *(integer)* | Number of body segments modeled in the thermal manikin. |
| - **`Control_Method`** *(string)* | Method used to control the PCS (e.g., manual, automatic). |
| - **`Ta`** *(number)* | Ambient air temperature (ﾂｰC). |
| - **`MRT`** *(number)* | Mean radiant temperature (ﾂｰC). |
| - **`RH`** *(number)* | Relative humidity (%). |
| - **`V`** *(number)* | Air velocity (m/s). |
| - **`Delta_Teq_`** *(object)* | Equivalent temperature change for specific body parts. Refer to *[#/definitions/BodyPart](#definitions/BodyPart)*. |
| - **`Delta_P_`** *(object)* | Change in perceived temperature or power supply for specific body parts. Refer to *[#/definitions/BodyPart](#definitions/BodyPart)*. |
| - **`Clo_`** *(object)* | Clothing insulation value for specific body parts. Refer to *[#/definitions/BodyPart](#definitions/BodyPart)*. |
| - **`Image_Path`** *(string)* | File path of related images. |
| - <a id="definitions/BodyPart"></a>**`BodyPart`** *(object)* | Body parts affected by PCS. |
<!-- METADATA_END -->

There is [an example PCS database](data/PCS_database_example.csv)
