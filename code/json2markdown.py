import json
from datetime import datetime
import configuration


def extract_properties(properties):
    """
    Extracts key, description, type, $ref, enum, and example from properties in the JSON schema.
    :param properties: Dictionary of properties from the JSON schema.
    :return: List of dictionaries containing key, description, type, and example.
    """
    extracted = []
    for key, attributes in properties.items():
        description = attributes.get("description", "No description available.")

        # Handle $ref (reference to another schema) - Make it a clickable link
        ref_info = attributes.get("$ref")
        if ref_info:
            description += f" [See {ref_info}]"

        # Handle enum (enumeration values)
        enum_info = attributes.get("enum", [])
        if enum_info:
            enum_str = ", ".join(map(str, enum_info))
            description += f" Must be one of: '{enum_str}'."

        # Handle example value
        example_info = attributes.get("example", "N/A")

        # Extract type information
        type_info = attributes.get("type", "Unknown")

        extracted.append({
            "key": key,
            "description": description,
            "type": type_info,
            "example": example_info
        })
    return extracted


def extract_definitions(definitions):
    """
    Extracts key, type, and properties (if available) from definitions in the JSON schema.
    :param definitions: Dictionary of definitions.
    :return: Formatted Markdown string for definitions.
    """
    if not definitions:
        return ""

    definition_content = "\n## Definitions\n"
    for key, attributes in definitions.items():
        type_info = attributes.get("type", "Unknown")

        # Handle $ref in definitions as a clickable link
        ref_info = attributes.get("$ref")
        ref_link = f" [See {ref_info}]" if ref_info else ""

        # Extract properties if available
        properties_info = attributes.get("properties", {})
        property_keys = ", ".join(f"`{p}`" for p in properties_info.keys()) if properties_info else "None"

        definition_content += f"- **`{key}`** *(type: {type_info})*{ref_link} - Properties: {property_keys}\n"

    return definition_content


def save_schema_as_markdown(json_file_path, markdown_file_path):
    """
    Converts a JSON schema to a Markdown file with a table of properties and definitions below it.
    :param json_file_path: Path to the JSON schema file.
    :param markdown_file_path: Path to save the Markdown formatted schema.
    """
    with open(json_file_path, "r", encoding="utf-8") as json_file:
        schema = json.load(json_file)

    # Extract properties under "columns" -> "properties"
    properties = schema.get("properties", {}).get("columns", {}).get("properties", {})
    extracted_data = extract_properties(properties)

    # Extract definitions separately
    definitions = schema.get("definitions", {})
    definitions_content = extract_definitions(definitions)

    # Add current datetime to the metadata
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    schema_description = schema.get("description", "Schema Description")
    schema_description += f" (Generated on {current_time})"

    # Construct Markdown table for properties
    markdown_content = f"# Database Metadata\n\n{schema_description}\n\n"
    markdown_content += "| Parameter | Type | Description | Example |\n|---|---|---|---|\n"

    for entry in extracted_data:
        markdown_content += f"| **`{entry['key']}`** | *{entry['type']}* | {entry['description']} | {entry['example']} |\n"

    # Append definitions
    markdown_content += definitions_content

    # Write Markdown file
    with open(markdown_file_path, "w", encoding="utf-8") as md_file:
        md_file.write(markdown_content)

    print(f"Markdown content successfully written to {markdown_file_path}")


def update_readme_with_metadata(readme_path, markdown_file_path):
    """
    Inserts metadata.markdown content into README.md as a table between METADATA_START and METADATA_END tags.
    """
    METADATA_START_TAG = "<!-- METADATA_START -->"
    METADATA_END_TAG = "<!-- METADATA_END -->"

    with open(markdown_file_path, "r", encoding="utf-8") as md_file:
        metadata_content = md_file.read()

    with open(readme_path, "r", encoding="utf-8") as readme_file:
        readme_lines = readme_file.readlines()

    new_readme_content = []
    inside_metadata_section = False
    metadata_found = False

    for line in readme_lines:
        if line.strip() == METADATA_START_TAG.strip():
            new_readme_content.append(line)
            new_readme_content.append(metadata_content + "\n")
            inside_metadata_section = True
            metadata_found = True
        elif line.strip() == METADATA_END_TAG.strip():
            inside_metadata_section = False
            new_readme_content.append(line)
        elif not inside_metadata_section:
            new_readme_content.append(line)

    if not metadata_found:
        new_readme_content.append("\n" + METADATA_START_TAG + "\n")
        new_readme_content.append(metadata_content + "\n")
        new_readme_content.append(METADATA_END_TAG + "\n")

    with open(readme_path, "w", encoding="utf-8") as readme_file:
        readme_file.writelines(new_readme_content)

    print("README.md successfully updated with metadata.")


if __name__ == "__main__":
    save_schema_as_markdown(
        json_file_path=configuration.METADATA_JSON_FILE_PATH,
        markdown_file_path=configuration.METADATA_MARKDOWN_FILE_PATH,
    )
    update_readme_with_metadata(
        readme_path=configuration.README_PATH,
        markdown_file_path=configuration.METADATA_MARKDOWN_FILE_PATH
    )
