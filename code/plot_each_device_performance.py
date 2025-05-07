import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import r2_score
from configuration import Config
from load_image import load_device_image
import warnings

# Suppress RankWarning from np.polyfit safely across NumPy versions
warnings.simplefilter("ignore", getattr(np, "RankWarning", Warning))


def select_default_level(available_levels):
    available_levels = sorted(available_levels)
    numeric_levels = [lvl for lvl in available_levels if lvl.lower().startswith("level") and lvl[5:].isdigit()]
    if numeric_levels:
        numeric_levels.sort(key=lambda x: int(x[5:]))
        return numeric_levels[len(numeric_levels) // 2]
    for preferred in ["Mid", "Low", "High"]:
        if preferred in available_levels:
            return preferred
    return available_levels[len(available_levels) // 2]


def select_default_angle(available_angles):
    numeric_angles = [a for a in available_angles if isinstance(a, (int, float)) and not pd.isna(a)]
    if not numeric_angles:
        return None
    numeric_angles.sort()
    return numeric_angles[len(numeric_angles) // 2]  # Select median


def select_target_area(df_row):
    delta_p_columns = [col for col in df_row.index if col.startswith("Delta_P_")]
    if not delta_p_columns:
        return None
    return max(delta_p_columns, key=lambda col: abs(df_row[col]))


def plot_dual_delta_p_with_theoretical_fit(df, target_id, body_part, level=None, angle=None, save=False):
    df_id = df[df["ID"] == target_id]
    available_levels = df_id["Level"].dropna().unique().tolist()
    if level is None or level not in available_levels:
        print(f"[ERROR] Level '{level}' is not available for ID {target_id}. Available: {available_levels}")
        return
    df_level = df_id[df_id["Level"] == level]

    if "Angle" in df_level.columns:
        available_angles = df_level["Angle"].dropna().unique().tolist()
        if angle is not None:
            if angle not in available_angles:
                print(f"[ERROR] Angle '{angle}' is not available for ID {target_id} and Level {level}. Available: {available_angles}")
                return
            df_level = df_level[df_level["Angle"] == angle]

    if df_level.empty:
        print(f"[ERROR] No data found for ID={target_id}, Level={level}, Angle={angle}")
        return

    delta_p_columns = [col for col in df.columns if col.startswith("Delta_P_")]
    body_labels = [col.replace("Delta_P_", "") for col in delta_p_columns]
    df_22 = df_level[df_level["Ta"] == 22]
    df_25 = df_level[df_level["Ta"] == 25]
    y_22 = df_22[delta_p_columns].mean().values
    y_25 = df_25[delta_p_columns].mean().values
    df_filtered = df_level[df_level[body_part].notna()]
    x_vals = df_filtered["Ta"].values
    y_vals = df_filtered[body_part].values
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
    if len(x_vals) > 1:
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

    title = f"Target Area vs Ta (ID={target_id}, Level={level}"
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
        save_path = os.path.join(Config.FIGURE_DIR, filename)
        plt.savefig(save_path)
        print(f"[SAVED] {save_path}")
    plt.close()


def main():
    file_path = os.path.join(Config.DataPaths.PROCESSED_DATA_DIR, "delta_results.csv")
    df = pd.read_csv(file_path)

    for target_id in range(1, 21):
        df_id = df[df["ID"] == target_id]
        available_levels = df_id["Level"].dropna().unique().tolist()
        if not available_levels:
            print(f"[SKIP] No Level data for ID {target_id}")
            continue
        level = select_default_level(available_levels)

        angle = None
        if "Angle" in df_id.columns:
            angle_candidates = df_id[df_id["Level"] == level]["Angle"].dropna().unique().tolist()
            angle = select_default_angle(angle_candidates)

        df_level = df_id[df_id["Level"] == level]
        if angle is not None:
            df_level = df_level[df_level["Angle"] == angle]
        if df_level.empty:
            continue

        sample_row = df_level.iloc[0]
        target_body_part = select_target_area(sample_row)
        if target_body_part is None:
            print(f"[SKIP] No Delta_P_* data found for ID {target_id}")
            continue

        plot_dual_delta_p_with_theoretical_fit(
            df,
            target_id=target_id,
            body_part=target_body_part,
            level=level,
            angle=angle,
            save=True
        )

if __name__ == "__main__":
    main()
