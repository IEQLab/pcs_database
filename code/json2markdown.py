# import os
# import json
# import jsonschema2md
# from datetime import datetime
# import configuration
#
# def save_schema_as_markdown(json_file_path, markdown_file_path):
#     """
#     Converts a JSON schema to a Markdown file and appends the current time to the description.
#
#     :param json_file_path: Path to the JSON schema file.
#     :param markdown_file_path: Path to save the Markdown formatted schema.
#     :return: None
#     """
#     parser = jsonschema2md.Parser(examples_as_yaml=False, show_examples="all")
#
#     with open(json_file_path, "r") as json_file:
#         schema = json.load(json_file)
#
#     # Add current datetime to the schema description
#     current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     if "description" in schema:
#         schema["description"] += f" (Generated on {current_time})"
#     else:
#         schema["description"] = f"Generated on {current_time}"
#
#     markdown_content = parser.parse_schema(schema)
#     formatted_markdown = f"# Database Metadata\n\n" + "".join(markdown_content)
#
#     with open(markdown_file_path, "w", encoding="utf-8") as md_file:
#         md_file.write(formatted_markdown)
#
#     print(f"Markdown content successfully written to {markdown_file_path}")
#
# def update_readme_with_metadata(readme_path, markdown_file_path):
#     """
#     Inserts metadata.markdown content into README.md as a table between METADATA_START and METADATA_END tags.
#     If the metadata is already up-to-date, no changes are made.
#     Ensures that the metadata is updated in-place without duplication.
#     """
#     METADATA_START_TAG = "<!-- METADATA_START -->"
#     METADATA_END_TAG = "<!-- METADATA_END -->"
#
#     with open(markdown_file_path, "r", encoding="utf-8") as md_file:
#         metadata_lines = md_file.readlines()
#
#     # Convert metadata into a Markdown table format
#     table_header = "| Key | Value |\n|---|---|\n"
#     table_rows = [f"| {line.split(':')[0].strip()} | {line.split(':')[1].strip()} |"
#                   for line in metadata_lines if ":" in line]
#     new_metadata_content = table_header + "\n".join(table_rows)
#
#     with open(readme_path, "r", encoding="utf-8") as readme_file:
#         readme_lines = readme_file.readlines()
#
#     new_readme_content = []
#     inside_metadata_section = False
#     existing_metadata = []
#     metadata_found = False
#
#     for line in readme_lines:
#         if line.strip() == METADATA_START_TAG.strip():
#             # Start of metadata section
#             inside_metadata_section = True
#             metadata_found = True
#             existing_metadata = []
#             new_readme_content.append(line)  # Keep METADATA_START tag
#         elif line.strip() == METADATA_END_TAG.strip():
#             # End of metadata section
#             inside_metadata_section = False
#             if existing_metadata and "\n".join(existing_metadata).strip() == new_metadata_content:
#                 # If existing metadata matches the new content, no update is needed
#                 print("README.md is already up-to-date. No changes made.")
#                 return
#             new_readme_content.append(new_metadata_content + "\n")
#             new_readme_content.append(line)  # Keep METADATA_END tag
#         elif inside_metadata_section:
#             # Collect existing metadata for comparison
#             existing_metadata.append(line.strip())
#         else:
#             # Keep other lines unchanged
#             new_readme_content.append(line)
#
#     # If metadata section is not found, add a new section at the end
#     if not metadata_found:
#         new_readme_content.append("\n" + METADATA_START_TAG + "\n")
#         new_readme_content.append(new_metadata_content + "\n")
#         new_readme_content.append(METADATA_END_TAG + "\n")
#
#     with open(readme_path, "w", encoding="utf-8") as readme_file:
#         readme_file.writelines(new_readme_content)
#
#     print("README.md successfully updated with metadata in table format.")
#
#
#
# if __name__ == "__main__":
#     save_schema_as_markdown(
#         json_file_path=configuration.METADATA_JSON_FILE_PATH,
#         markdown_file_path=configuration.METADATA_MARKDOWN_FILE_PATH,
#     )
#     update_readme_with_metadata(readme_path=configuration.README_PATH, markdown_file_path=configuration.METADATA_MARKDOWN_FILE_PATH)
#
import json
from datetime import datetime
import configuration


def extract_properties(properties):
    """
    Extracts key and description from properties in the JSON schema.
    :param properties: Dictionary of properties from the JSON schema.
    :return: List of (key, description) tuples.
    """
    extracted = []
    for key, attributes in properties.items():
        description = attributes.get("description", "No description available.")
        extracted.append((key, description))
    return extracted


def extract_definitions(definitions):
    """
    Extracts definitions from the JSON schema.
    :param definitions: Dictionary of definitions.
    :return: Formatted Markdown string for definitions.
    """
    if not definitions:
        return ""

    definition_content = "\n## Definitions\n"
    for key, attributes in definitions.items():
        description = attributes.get("description", "No description available.")
        definition_content += f"\n- <a id=\"definitions/{key}\"></a>**`{key}`** *(object)*: {description}\n"
        if "properties" in attributes:
            for sub_key in attributes["properties"]:
                definition_content += f"  - **`{sub_key}`** *(number)*\n"

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
    markdown_content += "| Parameter | Description |\n|---|---|\n"

    for key, description in extracted_data:
        markdown_content += f"| - **`{key}`** | {description} |\n"

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

