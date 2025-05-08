import os
import logging

# Define base project directory (two levels up from this file)
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

class Config:
    """Central configuration for directory structure and file paths."""

    PROJECT_DIR = PROJECT_DIR  # Optionally retain for reference

    README_PATH = os.path.join(PROJECT_DIR, "README.md")
    CODE_DIR = os.path.join(PROJECT_DIR, "code")
    FIGURE_DIR = os.path.join(PROJECT_DIR, "figure")

    class DataPaths:
        DATA_DIR = os.path.join(PROJECT_DIR, "data")
        RAW_DATA_DIR = os.path.join(DATA_DIR, "raw data")
        MANIKIN_DATA_DIR = os.path.join(RAW_DATA_DIR, "manikin_data")
        CHAMBER_DATA_DIR = os.path.join(RAW_DATA_DIR, "chamber_data")
        PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed_data")

        # Specific files
        METADATA_JSON_FILE = os.path.join(DATA_DIR, "metadata.json")
        METADATA_MARKDOWN_FILE = os.path.join(DATA_DIR, "metadata.markdown")
        DATABASE_CSV_FILE = os.path.join(DATA_DIR, "PCS_database.csv")

    class ImagePaths:
        IMAGE_DIR = os.path.join(PROJECT_DIR, "image")
        DEVICE_IMAGE_DIR = os.path.join(IMAGE_DIR, "device_image")
        EDITED_IMAGE_DIR = os.path.join(DEVICE_IMAGE_DIR, "edited_image")


# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
