import os
import logging
import matplotlib as mpl

# Define base project directory (two levels up from this file)
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class Config:
    """Central configuration for directory structure and file paths."""

    PROJECT_DIR = PROJECT_DIR  # Optionally retain for reference

    README_PATH = os.path.join(PROJECT_DIR, "README.md")
    CODE_DIR = os.path.join(PROJECT_DIR, "code")
    # FIGURE_DIR = os.path.join(PROJECT_DIR, "figure")

    class DataPaths:
        BASE_DIR = os.path.join(PROJECT_DIR, "data")
        RAW_DATA_DIR = os.path.join(BASE_DIR, "raw data")
        MANIKIN_DATA_DIR = os.path.join(RAW_DATA_DIR, "manikin_data")
        CHAMBER_DATA_DIR = os.path.join(RAW_DATA_DIR, "chamber_data")
        CLOTHING_DATA_DIR = os.path.join(RAW_DATA_DIR, "clothing_measurement_data")
        PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "processed_data")

        # Specific files
        METADATA_JSON_FILE = os.path.join(BASE_DIR, "metadata.json")
        METADATA_MARKDOWN_FILE = os.path.join(BASE_DIR, "metadata.markdown")
        DATABASE_CSV_FILE = os.path.join(BASE_DIR, "pcs_database.csv")

    class ImagePaths:
        BASE_DIR = os.path.join(PROJECT_DIR, "image")
        DEVICE_IMAGE_DIR = os.path.join(BASE_DIR, "device_image")
        EDITED_IMAGE_DIR = os.path.join(DEVICE_IMAGE_DIR, "edited_image")

    class FigurePaths:
        BASE_DIR = os.path.join(PROJECT_DIR, "figure")
        CLOTHING_DIR = os.path.join(BASE_DIR, "clothing_data")

    class PlotConfig:
        FONT_FAMILY = "Arial"
        FONT_SIZE_SMALL = 8
        FONT_SIZE_MEDIUM = 10
        FONT_SIZE_LARGE = 14
        FIG_SIZE = (9, 5)
        # COLOR_CYCLE = ["#1f77b4", "#ff7f0e"]

        @classmethod
        def apply(cls):
            mpl.rcParams["font.family"] = cls.FONT_FAMILY
            mpl.rcParams["font.size"] = cls.FONT_SIZE_MEDIUM
            mpl.rcParams["figure.figsize"] = cls.FIG_SIZE
            # mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=cls.COLOR_CYCLE)


# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
