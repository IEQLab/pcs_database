import pandas as pd
import json
from collections import OrderedDict
from manikin_body_part_names import BodyPart
import configuration as config

# Function to generate metadata template
def generate_metadata_template(body_parts, general_columns):
    metadata = OrderedDict()

    # Add general columns
    for column in general_columns:
        metadata[column["name"]] = {
            "description": column["description"],
            "type": column["type"],
            "unit": column.get("unit"),
            "category": column.get("category")
        }

    # Add all Delta_Teq columns first
    for body_part in body_parts:
        sanitized_name = body_part.replace(" ", "_")  # Replace spaces with underscores
        delta_teq_name = f"Delta_Teq_{sanitized_name}"
        metadata[delta_teq_name] = {
            "description": f"Delta equivalent temperature for {body_part}",
            "type": "float",
            "unit": "oC",
            "category": "body_temperature"
        }

    # Add all Clo columns after Delta_Teq
    for body_part in body_parts:
        sanitized_name = body_part.replace(" ", "_")  # Replace spaces with underscores
        clo_name = f"Clo_{sanitized_name}"
        metadata[clo_name] = {
            "description": f"Clo value for {body_part}",
            "type": "float",
            "unit": "clo",
            "category": "clothing"
        }

    return metadata


# Main process
if __name__ == "__main__":
    # Retrieve Body Parts
    manikin = BodyPart()
    body_parts = [value for key, value in vars(manikin).items()]

    # Define general columns
    general_columns = [
        {"name": "DateTime", "description": "Timestamp of the record", "type": "datetime", "unit": None,
         "category": "time"},
        {"name": "Place", "description": "Measurement place", "type": "string", "unit": None,
         "category": "place"},
        {"name": "PCS", "description": "Personal Comfort System", "type": "string", "unit": None,
         "category": "comfort"},
        {"name": "State", "description": "State of manikin", "type": "string", "unit": None,
         "category": "state"},
        {"name": "Situation", "description": "Simulated situation", "type": "string", "unit": None,
         "category": "state"},
        {"name": "Ta", "description": "Air temperature", "type": "float", "unit": "oC", "category": "environment"},
        {"name": "MRT", "description": "Mean Radiant Temperature", "type": "float", "unit": "oC",
         "category": "environment"},
        {"name": "RH", "description": "Relative Humidity", "type": "float", "unit": "%", "category": "environment"},
        {"name": "V", "description": "Air velocity", "type": "float", "unit": "m/s", "category": "environment"},
        {"name": "Clo", "description": "Clothing insulation", "type": "float", "unit": "clo", "category": "clothing"},
        {"name": "Posture", "description": "Posture of the subject", "type": "string", "unit": None,
         "category": "state"}
    ]

    # Generate metadata
    metadata = generate_metadata_template(body_parts, general_columns)

    # Save metadata as a JSON file
    metadata_file = config.METADATA_FILE
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=4)
    print(f"Metadata saved to {metadata_file}")

    # Generate an empty DataFrame and save it as a CSV file
    columns = list(metadata.keys())
    df = pd.DataFrame(columns=columns)
    csv_file = config.DATABASE_CSV_FILE
    df.to_csv(csv_file, index=False)
    print(f"Empty CSV with metadata columns saved to {csv_file}")
