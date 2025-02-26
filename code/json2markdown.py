import os
import json
import jsonschema2md
from datetime import datetime
import configuration

def save_schema_as_markdown(json_file_path, markdown_file_path):
    """
    Converts a JSON schema to a Markdown file and appends the current time to the description.

    :param json_file_path: Path to the JSON schema file.
    :param markdown_file_path: Path to save the Markdown formatted schema.
    :return: None
    """
    parser = jsonschema2md.Parser(examples_as_yaml=False, show_examples="all")

    with open(json_file_path, "r") as json_file:
        schema = json.load(json_file)

    # Add current datetime to the schema description
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "description" in schema:
        schema["description"] += f" (Generated on {current_time})"
    else:
        schema["description"] = f"Generated on {current_time}"

    markdown_content = parser.parse_schema(schema)
    formatted_markdown = f"# Database Metadata\n\n" + "".join(markdown_content)

    with open(markdown_file_path, "w", encoding="utf-8") as md_file:
        md_file.write(formatted_markdown)

    print(f"Markdown content successfully written to {markdown_file_path}")

def update_readme_with_metadata(readme_path, markdown_file_path):
    """
    Inserts metadata.markdown content into README.md as a table between METADATA_START and METADATA_END tags.
    If the metadata is already up-to-date, no changes are made.
    Ensures that the metadata is updated in-place without duplication.
    """
    METADATA_START_TAG = "<!-- METADATA_START -->"
    METADATA_END_TAG = "<!-- METADATA_END -->"

    with open(markdown_file_path, "r", encoding="utf-8") as md_file:
        metadata_lines = md_file.readlines()

    # Convert metadata into a Markdown table format
    table_header = "| Key | Value |\n|---|---|\n"
    table_rows = [f"| {line.split(':')[0].strip()} | {line.split(':')[1].strip()} |"
                  for line in metadata_lines if ":" in line]
    new_metadata_content = table_header + "\n".join(table_rows)

    with open(readme_path, "r", encoding="utf-8") as readme_file:
        readme_lines = readme_file.readlines()

    new_readme_content = []
    inside_metadata_section = False
    existing_metadata = []
    metadata_found = False

    for line in readme_lines:
        if line.strip() == METADATA_START_TAG.strip():
            # Start of metadata section
            inside_metadata_section = True
            metadata_found = True
            existing_metadata = []
            new_readme_content.append(line)  # Keep METADATA_START tag
        elif line.strip() == METADATA_END_TAG.strip():
            # End of metadata section
            inside_metadata_section = False
            if existing_metadata and "\n".join(existing_metadata).strip() == new_metadata_content:
                # If existing metadata matches the new content, no update is needed
                print("README.md is already up-to-date. No changes made.")
                return
            new_readme_content.append(new_metadata_content + "\n")
            new_readme_content.append(line)  # Keep METADATA_END tag
        elif inside_metadata_section:
            # Collect existing metadata for comparison
            existing_metadata.append(line.strip())
        else:
            # Keep other lines unchanged
            new_readme_content.append(line)

    # If metadata section is not found, add a new section at the end
    if not metadata_found:
        new_readme_content.append("\n" + METADATA_START_TAG + "\n")
        new_readme_content.append(new_metadata_content + "\n")
        new_readme_content.append(METADATA_END_TAG + "\n")

    with open(readme_path, "w", encoding="utf-8") as readme_file:
        readme_file.writelines(new_readme_content)

    print("README.md successfully updated with metadata in table format.")



if __name__ == "__main__":
    save_schema_as_markdown(
        json_file_path=configuration.METADATA_JSON_FILE_PATH,
        markdown_file_path=configuration.METADATA_MARKDOWN_FILE_PATH,
    )
    update_readme_with_metadata(readme_path=configuration.README_PATH, markdown_file_path=configuration.METADATA_MARKDOWN_FILE_PATH)