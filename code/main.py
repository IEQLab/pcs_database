import os
from visualization import plot_overall_pcs_effects
from config.configuration import Config
from data_processing import preprocess_manikin, database_columns_names


def main():
    """
    Main function to execute the workflow:
    1. Generate columns and save them as a CSV file.
    2. Generate metadata and save it as a JSON and CSV file.
    3. Plot PCS effects based on processed data.
    """
    # Step 1: Generate and save columns format
    print("Step 1: Generating columns format...")
    database_columns_names.main()

    # Step 2: Preprocess the database and generate metadata
    print("Step 2: Preprocessing the database and generating metadata...")
    preprocess_manikin.main()


if __name__ == "__main__":
    main()
