import os

# Project directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw data")
MANIKIN_DATA_DIR = os.path.join(RAW_DATA_DIR, "manikin_data")
CHAMBER_DATA_DIR = os.path.join(RAW_DATA_DIR, "chamber_data")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed_data")
CODE_DIR = os.path.join(PROJECT_DIR, "code")
FIGURE_DIR = os.path.join(PROJECT_DIR, "figure")

# Paths for specific files
METADATA_FILE = os.path.join(DATA_DIR, "metadata.json")
DATABASE_CSV_FILE = os.path.join(DATA_DIR, "PCS_database.csv")
