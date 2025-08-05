"""
This code visualizes the overall heating/cooling effects of PCS by plotting Delta ht values
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import r2_score
from code.config.configuration import Config
from code.utils.image_loader import load_device_image


def plot_delta_teq():
    """
    Plot Delta Teq by Body Parts for each condition in the dataset.
    """
    # Define file path for the processed data
    teq_file_path = os.path.join(
        Config.DataPaths.PROCESSED_DATA_DIR, "delta_teq.csv"
    )  # Adjust path if necessary

    # Check if the file exists
    if not os.path.exists(teq_file_path):
        print(f"File not found: {teq_file_path}")
        return

    # Load the CSV data
    teq_data = pd.read_csv(teq_file_path)

    # Remove columns corresponding to Group A and Group B from the plot
    columns_to_plot = [
        col for col in teq_data.columns if "Delta_Teq_" in col and "Group" not in col
    ]
    body_parts_filtered = [col.replace("Delta_Teq_", "") for col in columns_to_plot]
    y_values_filtered = teq_data[columns_to_plot]  # Filtered Y-axis values
    conditions = teq_data["Condition2"]  # Legend labels

    # Plot
    plt.figure(figsize=(12, 6))
    for i, row in y_values_filtered.iterrows():
        plt.plot(body_parts_filtered, row.values, marker="o", label=conditions.iloc[i])

    # Customize plot
    plt.title("Delta Teq by Body Parts", fontsize=16)
    plt.xlabel("Body Parts", fontsize=12)
    plt.ylabel("Delta Teq", fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(title="Condition2", fontsize=10)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Show plot
    plt.tight_layout()
    plt.savefig(os.path.join(Config.FIGURE_DIR, "example_plot.svg"))
    plt.savefig(os.path.join(Config.FIGURE_DIR, "example_plot.pdf"))
    plt.show()


def select_default_level(available_levels):
    """
    Select a default level from a list of available levels.
    Priority:
        1. Numeric levels like 'Level1', 'Level2', etc. -> choose middle
        2. Named levels like 'Low', 'Mid', 'High' -> prefer 'Mid'
        3. Otherwise -> choose the middle alphabetically
    """
    available_levels = sorted(available_levels)
    numeric_levels = [
        lvl
        for lvl in available_levels
        if lvl.lower().startswith("level") and lvl[5:].isdigit()
    ]
    if numeric_levels:
        numeric_levels.sort(key=lambda x: int(x[5:]))
        return numeric_levels[len(numeric_levels) // 2]
    for preferred in ["Mid", "Low", "High"]:
        if preferred in available_levels:
            return preferred
    return available_levels[len(available_levels) // 2]


def main():
    file_path = os.path.join(Config.DataPaths.BASE_DIR, "pcs_database.csv")
    df = pd.read_csv(file_path)


if __name__ == "__main__":
    main()
