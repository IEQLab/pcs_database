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
    teq_file_path = os.path.join(Config.DataPaths.PROCESSED_DATA_DIR, "delta_teq.csv")  # Adjust path if necessary

    # Check if the file exists
    if not os.path.exists(teq_file_path):
        print(f"File not found: {teq_file_path}")
        return

    # Load the CSV data
    teq_data = pd.read_csv(teq_file_path)

    # Remove columns corresponding to Group A and Group B from the plot
    columns_to_plot = [col for col in teq_data.columns if "Delta_Teq_" in col and "Group" not in col]
    body_parts_filtered = [col.replace("Delta_Teq_", "") for col in columns_to_plot]
    y_values_filtered = teq_data[columns_to_plot]  # Filtered Y-axis values
    conditions = teq_data["Condition2"]  # Legend labels

    # Plot
    plt.figure(figsize=(12, 6))
    for i, row in y_values_filtered.iterrows():
        plt.plot(body_parts_filtered, row.values, marker='o', label=conditions.iloc[i])


    # Customize plot
    plt.title("Delta Teq by Body Parts", fontsize=16)
    plt.xlabel("Body Parts", fontsize=12)
    plt.ylabel("Delta Teq", fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(title="Condition2", fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

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
    numeric_levels = [lvl for lvl in available_levels if lvl.lower().startswith("level") and lvl[5:].isdigit()]
    if numeric_levels:
        numeric_levels.sort(key=lambda x: int(x[5:]))
        return numeric_levels[len(numeric_levels) // 2]
    for preferred in ["Mid", "Low", "High"]:
        if preferred in available_levels:
            return preferred
    return available_levels[len(available_levels) // 2]

def plot_dual_delta_p_with_theoretical_fit(df, target_id, body_part="Delta_P_Left Chest", level=None, angle=None, save=False):
    """
    Generate a 3-panel figure:
    - Left: Device image
    - Center: Bar plot of ∆P for all body parts
    - Right: Scatter plot with regression lines
    """
    df_id = df[df["ID"] == target_id]
    available_levels = df_id["Level"].dropna().unique().tolist()
    if level is None:
        print(f"[INFO] Available Level values for ID {target_id}: {available_levels}")
        return
    if level not in available_levels:
        print(f"[ERROR] Level '{level}' is not available for ID {target_id}. Available: {available_levels}")
        return
    df_level = df_id[df_id["Level"] == level]

    if "Angle" in df_level.columns:
        available_angles = df_level["Angle"].dropna().unique().tolist()
        if angle is not None and angle not in available_angles:
            print(f"[ERROR] Angle '{angle}' is not available for ID {target_id} and Level {level}. Available: {available_angles}")
            return
        if angle is not None:
            df_level = df_level[df_level["Angle"] == angle]

    if df_level.empty:
        print(f"[ERROR] No data found for ID={target_id}, Level={level}, Angle={angle}")
        return

    delta_p_columns = [col for col in df.columns if col.startswith("Delta_P_")]
    body_labels = [col.replace("Delta_P_", "") for col in delta_p_columns]

    df_22 = df_level[df_level["Tset"] == 22]
    df_25 = df_level[df_level["Tset"] == 25]
    y_22 = df_22[delta_p_columns].mean().values
    y_25 = df_25[delta_p_columns].mean().values

    df_filtered = df_level[df_level["Delta_P_Crown"].notna()]
    x_vals = df_filtered["PCS_Ta"].values
    y_vals = df_filtered["Delta_P_Crown"].values

    all_y_values = np.concatenate([y_22, y_25, y_vals])
    all_y_values = all_y_values[~np.isnan(all_y_values)]
    if all_y_values.size == 0:
        print("[ERROR] No valid ∆P data found for selected conditions.")
        return

    y_min, y_max = np.floor(all_y_values.min()), np.ceil(all_y_values.max())
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), gridspec_kw={'width_ratios': [1, 2, 2]})

    image_path = load_device_image(target_id)
    if image_path is not None:
        try:
            image = plt.imread(image_path)
            axes[0].imshow(image)
            axes[0].axis('off')
            axes[0].set_title(f"Device Image\n(ID={target_id})", fontsize=12)
        except Exception as e:
            print(f"[WARNING] Failed to load image: {image_path}, error: {e}")
            axes[0].axis('off')
    else:
        axes[0].axis('off')
        axes[0].text(0.5, 0.5, "No Image", ha='center', va='center', fontsize=12)

    x = range(len(delta_p_columns))
    width = 0.35
    axes[1].bar([i - width / 2 for i in x], y_22, width=width, label="Ta=22°C")
    axes[1].bar([i + width / 2 for i in x], y_25, width=width, label="Ta=25°C")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(body_labels, rotation=90)
    axes[1].set_ylabel("∆P [W/m²]")
    axes[1].set_ylim(y_min, y_max)
    axes[1].set_title(f"Body Part-wise ∆P (ID={target_id})")
    axes[1].legend()
    axes[1].grid(True)

    axes[2].scatter(x_vals, y_vals, color='blue', label='Observed')
    m_exp, b_exp = np.polyfit(x_vals, y_vals, 1)
    y_pred_exp = m_exp * x_vals + b_exp
    r2_exp = r2_score(y_vals, y_pred_exp)
    x_fit = np.linspace(20, x_vals.max() + 1, 100)
    y_fit_exp = m_exp * x_fit + b_exp
    axes[2].plot(x_fit, y_fit_exp, 'r-', label=f'Experimental Fit: P={m_exp:.2f}·Ta{b_exp:+.2f} (R²={r2_exp:.3f})')

    X_theory = x_vals - 34
    hc_theory = np.dot(X_theory, y_vals) / np.dot(X_theory, X_theory)
    y_fit_theory = hc_theory * (x_fit - 34)
    y_pred_theory = hc_theory * (x_vals - 34)
    r2_theory = r2_score(y_vals, y_pred_theory)
    axes[2].plot(x_fit, y_fit_theory, 'g--', label=f'Theoretical Fit: P={hc_theory:.2f}·(Ta-34) (R²={r2_theory:.3f})')

    axes[2].axvline(x=0, color='black', linestyle=':')
    axes[2].axvline(x=34, color='gray', linestyle='--')

    title = f"Delta_P_Crown vs Ta (ID={target_id}, Level={level}"
    if angle is not None:
        title += f", Angle={angle}"
    title += ")"

    axes[2].set_title(title)
    axes[2].set_xlabel("Air Temperature Ta [°C]")
    axes[2].set_ylabel("∆P [W/m²]")
    axes[2].set_ylim(y_min, y_max)
    axes[2].set_xlim(left=20)
    axes[2].legend()
    axes[2].grid(True)

    plt.tight_layout()
    if save:
        filename = f"delta_p_plot_ID{target_id}.svg"
        save_path = os.path.join(Config.FigurePaths.BASE_DIR, filename)
        plt.savefig(save_path)
        print(f"[SAVED] {save_path}")
    plt.close()

def main():
    file_path = os.path.join(Config.DataPaths.PROCESSED_DATA_DIR, "delta_results.csv")
    df = pd.read_csv(file_path)
    body_part = "Delta_P_Crown"
    angle = 135

    for target_id in range(1, 20):
        df_id = df[df["ID"] == target_id]
        available_levels = df_id["Level"].dropna().unique().tolist()
        if not available_levels:
            print(f"[SKIP] No Level data for ID {target_id}")
            continue
        level = select_default_level(available_levels)
        plot_dual_delta_p_with_theoretical_fit(
            df,
            target_id=target_id,
            body_part=body_part,
            level=level,
            angle=angle,
            save=True
        )

if __name__ == "__main__":
    main()

