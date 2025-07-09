# Database Metadata

Schema Description (Generated on 2025-07-09 14:28:57)

| Parameter | Type | Description | Example |
|---|---|---|---|
| **`PCS_ID`** | *integer* | Unique PCS identifier (integer number) | 1 |
| **`Category`** | *string* | Category of the PCS. Must be one of: `Cooling, Heating`. | Cooling |
| **`Physical_Effect`** | *string* | Physical effect of the PCS. Must be one or more: Convective, Conductive, Radiant, Evaporative. | Convective |
| **`Type`** | *string* | Type of PCS (e.g., fan, foot warmer). | Small desk fan |
| **`Size`** | *number* | PCS dimensions in the following format: height, length, width (cm) | 20, 20, 3 |
| **`Brand`** | *string* | Brand name of the PCS. If it is a prototype, give it a name. | Simpeak |
| **`Product_Reference`** | *string* | Reference product URL or project landing page. | http://... |
| **`Availability`** | *string* | Market availability. Must be one of: `Market-ready, Prototype`. | Market-ready |
| **`Image`** | *string* | Name of the image file of the PCS in JPEG or PNG format (preference for high resolution 300dpi) | example.jpg |
| **`Publication`** | *string* | DOI or URL for a publication where this data is presented. | 10.53540/tjer.vol18iss2pp62-71 |
| **`PCS_Level`** | *string* | Selected level for the test/total PEC control available levels. Example, for a fan with 10 speed levels, level 3 is selected: 3/10. | Low |
| **`Price_USD`** | *number* | Price of the PCS in US dollars. | 10 |
| **`Year`** | *number* | Year of the study | 10 |
| **`Angle_Horizontal`** | *number* | Horizontal angle between the middle of PCS and the middle of target body part (degrees). | 125.0 |
| **`Distance_Horizontal`** | *number* | Horizontal distance between the middle of the PCS and target body part (cm). | 60.0 |
| **`Distance_Vertical`** | *number* | Vertical distance between the middle of the PCS and target body part (cm). | 10.0 |
| **`Target_Body`** | *string* | Body Segment targeted by PCS. | Face |
| **`Plug_Power`** | *number* | Power supply of the PCS (W).  | 10 |
| **`Research_Center`** | *string* | Facility where the measurement was taken. | The University of Sydney |
| **`Country`** | *string* | Country where the study was performed. | Australia |
| **`Posture`** | *string* | Posture of the manikin during measurement (e.g., standing, sitting). | Sitting |
| **`Context`** | *string* | Type of building or vehicle considered in the experiment (e.g., office, car). | Office |
| **`Manikin_Company`** | *string* | Manufacturer of the thermal manikin used. | PT Manikins |
| **`Manikin_Type`** | *string* | Manikin capability. Non-wired manikins should not be included. Must be one of: `Thermal, Sweating`. | Thermal |
| **`Manikin_Gender`** | *string* | Gender representation of the thermal manikin. Must be one of: `Male, Female`. | Female |
| **`Manikin_Body_Segments`** | *integer* | Number of body segments of the thermal manikin. | 22 |
| **`Control_Method`** | *string* | Method used to control the PCS (e.g., manual, automatic). Must be one of: `TskControl, HeatFluxControl, ComfortControl`. | TskControl |
| **`{Condition}_Ta`** | *number* | Ambient air temperature (°C). | 25 |
| **`{Condition}_MRT`** | *number* | Mean radiant temperature (°C). | 25 |
| **`{Condition}_RH`** | *number* | Relative humidity (%). | 50 |
| **`{Condition}_V`** | *number* | Air velocity (m/s). Body part information follows this parameter. See: `#/definitions/Condition` | 0.1 |
| **`{Condition}_Tsk_{BodyPart}`** | *number* | Skin temperature for each body part(°C). Body part information follows this parameter. See: `#/definitions/Condition and #/definitions/BodyPart` | 34 |
| **`{Condition}_P_{BodyPart}`** | *number* | Power supply for each body part (W). Body part information follows this parameter. See: `#/definitions/Condition and #/definitions/BodyPart` | 100 |
| **`Delta_Teq_{BodyPart}`** | *number* | Change in equivalent temperature for each body part (°C). Body part information follows this parameter. See: `#/definitions/BodyPart` | 1 |
| **`Delta_P_{BodyPart}`** | *number* | Change in power supply from the manikin for each body part (W). Body part information follows this parameter. See: `#/definitions/BodyPart` | 10 |
| **`Clo_{BodyPart}`** | *number* | Clothing insulation for each body part. Body part information follows this parameter. See: `#/definitions/BodyPart` | 1 |
| **`Condition_without_PCS`** | *string* | File path to the raw data without PCS. | ID0_NoPCS.csv |
| **`Condition_with_PCS`** | *string* | File path to the raw data with PCS. | ID1_Small desk fan (grey).csv |

## Definitions
- **`BodyPart`** *(type: object)* - Properties: `Crown`, `Head`, `Left_Chest`, `Right_Chest`, `Left_Back`, `Right_Back`, `Abdomen`, `Buttocks`, `Left_Upper_Arm`, `Right_Upper_Arm`, `Left_Forearm`, `Right_Forearm`, `Left_Hand`, `Right_Hand`, `Left_Front_Thigh`, `Right_Front_Thigh`, `Left_Back_Thigh`, `Right_Back_Thigh`, `Left_Lower_Leg`, `Right_Lower_Leg`, `Left_Foot`, `Right_Foot`
- **`Condition`** *(type: object)* - Properties: `Baseline`, `PCS`
