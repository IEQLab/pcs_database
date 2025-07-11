import os
from visualization import plot_pcs_effects
from config import database_columns_names
from config.configuration import Config
from data_processing import preprocess_manikin


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

    # Step 3: Plot PCS effects
    print("Step 3: Plotting PCS effects...")
    if os.path.exists(
        os.path.join(Config.DataPaths.PROCESSED_DATA_DIR, "delta_teq.csv")
    ):
        plot_pcs_effects.main()
    else:
        print("Processed data (delta_teq.csv) not found. Skipping plotting.")


if __name__ == "__main__":
    main()
