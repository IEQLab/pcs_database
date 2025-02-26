import os
import json
import jsonschema2md
from datetime import datetime
import configuration

METADATA_START_TAG = "<!-- METADATA_START -->\n"
METADATA_END_TAG = "<!-- METADATA_END -->\n"

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
    Inserts metadata.markdown content into README.md between METADATA_START and METADATA_END tags.
    """
    with open(markdown_file_path, "r", encoding="utf-8") as md_file:
        metadata_content = md_file.read()

    with open(readme_path, "r", encoding="utf-8") as readme_file:
        readme_lines = readme_file.readlines()

    new_readme_content = []
    inside_metadata_section = False

    for line in readme_lines:
        if line.strip() == METADATA_START_TAG.strip():
            new_readme_content.append(line)
            new_readme_content.append(metadata_content + "\n")  # メタデータを追加
            inside_metadata_section = True
        elif line.strip() == METADATA_END_TAG.strip():
            inside_metadata_section = False
            new_readme_content.append(line)  # 終了タグを追加
        elif not inside_metadata_section:
            new_readme_content.append(line)  # 既存の行をそのまま保持

    # METADATA タグがなかった場合、新しく追加
    if METADATA_START_TAG.strip() not in readme_lines:
        new_readme_content.append("\n" + METADATA_START_TAG)
        new_readme_content.append(metadata_content + "\n")
        new_readme_content.append(METADATA_END_TAG)
    else:
        pass

    with open(readme_path, "w", encoding="utf-8") as readme_file:
        readme_file.writelines(new_readme_content)

    print(f"README.md successfully updated with metadata.")

if __name__ == "__main__":
    save_schema_as_markdown(
        json_file_path=configuration.METADATA_JSON_FILE_PATH,
        markdown_file_path=configuration.METADATA_MARKDOWN_FILE_PATH,
    )
    update_readme_with_metadata(readme_path=configuration.README_PATH, markdown_file_path=configuration.METADATA_MARKDOWN_FILE_PATH)