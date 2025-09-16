import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import r2_score
import warnings

# Add the project root directory to sys.path
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

# Add the code directory to sys.path
code_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, code_dir)

from config.configuration import Config
from utils.image_loader import load_device_image
from config.columns import Columns

# Suppress RankWarning from np.polyfit safely across NumPy versions
warnings.simplefilter("ignore", getattr(np, "RankWarning", Warning))

# TODO: Add each device performance to the whole body
PCS_ID_COL = Columns.PCS_ID
PCS_LEVEL_COL = Columns.PCS_Level


def select_default_level(available_levels):
    available_levels = sorted(available_levels)
    # Handle numeric levels (float values like 0.5, 1.0, etc.)
    numeric_levels = [
        lvl for lvl in available_levels 
        if isinstance(lvl, (int, float)) and not pd.isna(lvl)
    ]
    if numeric_levels:
        numeric_levels.sort()
        return numeric_levels[len(numeric_levels) // 2]
        
    # Handle string levels
    string_levels = [
        lvl for lvl in available_levels 
        if isinstance(lvl, str) and lvl.lower().startswith("level") and lvl[5:].isdigit()
    ]
    if string_levels:
        string_levels.sort(key=lambda x: int(x[5:]))
        return string_levels[len(string_levels) // 2]
        
    # Handle named levels
    for preferred in ["Mid", "Low", "High"]:
        if preferred in available_levels:
            return preferred
    return available_levels[len(available_levels) // 2]


def select_default_angle(available_angles):
    numeric_angles = [
        a for a in available_angles if isinstance(a, (int, float)) and not pd.isna(a)
    ]
    if not numeric_angles:
        return None
    numeric_angles.sort()
    return numeric_angles[len(numeric_angles) // 2]  # Select median


def select_target_area(df_row):
    delta_p_columns = [col for col in df_row.index if col.startswith("Delta_P_")]
    if not delta_p_columns:
        return None
    return max(delta_p_columns, key=lambda col: abs(df_row[col]))


def extract_data_with_threshold(df, column_name, value, threshold=1.0):
    """Extracts data from a DataFrame where the specified column's value is within a given range."""
    if column_name not in df.columns:
        print(f"[ERROR] Column '{column_name}' not found in DataFrame.")
        return pd.DataFrame()

    filtered_df = df[
        (df[column_name] >= value - threshold) & (df[column_name] <= value + threshold)
    ]
    if filtered_df.empty:
        print(
            f"[WARNING] No data found with {column_name} in range [{value - threshold}, {value + threshold}]."
        )
    return filtered_df


def calculate_delta_ht_from_regression(df_data, delta_p_col, ta_col, reference_ta=34.0):
    """
    Calculate delta_ht from Air Temperature vs Delta_P regression.
    Uses linear regression through reference temperature (Ta=34°C where Delta_P=0).
    
    Args:
        df_data: DataFrame with temperature and delta_P data
        delta_p_col: Column name for Delta_P values
        ta_col: Column name for air temperature values
        reference_ta: Reference temperature where delta_P = 0 [°C]
        
    Returns:
        delta_ht: Heat transfer coefficient change [W/m²/°C] (slope of regression line)
    """
    if delta_p_col not in df_data.columns or ta_col not in df_data.columns:
        return np.nan
        
    # Filter valid data points
    valid_mask = df_data[delta_p_col].notna() & df_data[ta_col].notna()
    valid_data = df_data[valid_mask]
    
    if len(valid_data) < 2:
        return np.nan
    
    ta_values = valid_data[ta_col].values
    delta_p_values = valid_data[delta_p_col].values
    
    # Linear regression forced through reference point (reference_ta, 0)
    # Delta_P = delta_ht * (Ta - reference_ta)
    # So delta_ht = Delta_P / (Ta - reference_ta)
    ta_adjusted = ta_values - reference_ta
    
    # Avoid division by zero
    non_zero_mask = ta_adjusted != 0
    if not np.any(non_zero_mask):
        return np.nan
    
    ta_adjusted = ta_adjusted[non_zero_mask]
    delta_p_adjusted = delta_p_values[non_zero_mask]
    
    # Calculate slope using least squares: delta_ht = sum(Ta_adj * Delta_P) / sum(Ta_adj^2)
    if len(ta_adjusted) == 0:
        return np.nan
        
    delta_ht = np.sum(ta_adjusted * delta_p_adjusted) / np.sum(ta_adjusted ** 2)
    
    return delta_ht


def plot_local_pcs_effects_with_temperatures(
    df, target_id, level=None, angle=None, save=False
):
    """
    Plot Delta_Teq values for different body segments at three temperatures (22°C, 25°C, 28°C).
    Left panel shows device image, right panel shows Delta_Teq bar chart.
    """
    df_id = df[df[Columns.PCS_ID] == target_id]
    available_levels = df_id[Columns.PCS_Level].dropna().unique().tolist()
    if level is None or level not in available_levels:
        print(
            f"[ERROR] Level '{level}' is not available for ID {target_id}. Available: {available_levels}"
        )
        return
    df_level = df_id[df_id[Columns.PCS_Level] == level]

    if Columns.Angle_Horizontal in df_level.columns:
        available_angles = df_level[Columns.Angle_Horizontal].dropna().unique().tolist()
        if angle is not None:
            if angle not in available_angles:
                print(
                    f"[ERROR] Angle '{angle}' is not available for ID {target_id} and Level {level}. Available: {available_angles}"
                )
                return
            df_level = df_level[df_level[Columns.Angle_Horizontal] == angle]

    if df_level.empty:
        print(f"[ERROR] No data found for ID={target_id}, Level={level}, Angle={angle}")
        return

    # Get Delta_Teq columns for body segments
    delta_teq_columns = [col for col in df.columns if col.startswith("Delta_Teq_")]
    body_labels = [col.replace("Delta_Teq_", "") for col in delta_teq_columns]
    
    # Get corresponding Delta_P columns for delta_ht calculation
    delta_p_columns = [col.replace("Delta_Teq_", "Delta_P_") for col in delta_teq_columns]
    # Filter to only include existing Delta_P columns, maintaining alignment
    delta_p_columns = [col if col in df.columns else None for col in delta_p_columns]
    
    # Get corresponding Tsk columns (use PCS_Tsk as representative skin temperature)
    tsk_columns = [col.replace("Delta_Teq_", "PCS_Tsk_") for col in delta_teq_columns]
    # For overall, use PCS_Tsk_All; filter to only include existing Tsk columns
    tsk_columns = [col if col in df.columns else "PCS_Tsk_All" for col in tsk_columns]
    
    # Extract data for three temperature conditions with tolerance
    df_22 = extract_data_with_threshold(
        df=df_level, column_name=Columns.PCS_Ta, value=22, threshold=1
    )
    df_25 = extract_data_with_threshold(
        df=df_level, column_name=Columns.PCS_Ta, value=25, threshold=1
    )
    df_28 = extract_data_with_threshold(
        df=df_level, column_name=Columns.PCS_Ta, value=28, threshold=1
    )
    
    # Calculate mean Delta_Teq values for each temperature condition
    y_22 = df_22[delta_teq_columns].mean().values if not df_22.empty else np.zeros(len(delta_teq_columns))
    y_25 = df_25[delta_teq_columns].mean().values if not df_25.empty else np.zeros(len(delta_teq_columns))
    y_28 = df_28[delta_teq_columns].mean().values if not df_28.empty else np.zeros(len(delta_teq_columns))
    
    # Calculate delta_ht values for each body part using regression across all temperatures
    delta_ht_values = np.zeros(len(delta_teq_columns))
    
    for i, (delta_teq_col, delta_p_col, tsk_col) in enumerate(zip(delta_teq_columns, delta_p_columns, tsk_columns)):
        if delta_p_col is not None and delta_p_col in df.columns:
            # Use all temperature data for regression
            delta_ht_values[i] = calculate_delta_ht_from_regression(
                df_level, delta_p_col, Columns.PCS_Ta, reference_ta=34.0
            )
    
    # Check if we have valid data
    if df_22.empty and df_25.empty and df_28.empty:
        print(f"[ERROR] No valid Delta_Teq data found for ID {target_id}")
        return

    # Calculate y-axis limits for Delta_Teq
    all_y_values = np.concatenate([y_22, y_25, y_28])
    all_y_values = all_y_values[~np.isnan(all_y_values)]
    if all_y_values.size == 0:
        print("[ERROR] No valid ∆Teq data found for selected conditions.")
        return

    # Calculate y-axis limits for Delta_Teq with appropriate margins
    all_y_values = np.concatenate([y_22, y_25, y_28])
    all_y_values = all_y_values[~np.isnan(all_y_values)]
    if all_y_values.size == 0:
        print("[ERROR] No valid ∆Teq data found for selected conditions.")
        return

    # Calculate reasonable axis limits with 10-20% margin
    y_data_min, y_data_max = all_y_values.min(), all_y_values.max()
    y_range = y_data_max - y_data_min
    
    if y_range == 0:  # All values are the same
        y_margin = max(abs(y_data_min) * 0.1, 0.5)  # At least 0.5 degree margin
        y_min, y_max = y_data_min - y_margin, y_data_max + y_margin
    else:
        y_margin = y_range * 0.15  # 15% margin on each side
        y_min, y_max = y_data_min - y_margin, y_data_max + y_margin
    
    # Calculate y-axis limits for delta_ht (second y-axis) with appropriate margins
    all_ht_values = delta_ht_values[~np.isnan(delta_ht_values) & (delta_ht_values != 0)]
    
    if all_ht_values.size > 0:
        ht_data_min, ht_data_max = all_ht_values.min(), all_ht_values.max()
        ht_range = ht_data_max - ht_data_min
        
        if ht_range == 0:  # All values are the same
            ht_margin = max(abs(ht_data_min) * 0.1, 0.1)  # At least 0.1 W/m²/°C margin
            ht_min, ht_max = ht_data_min - ht_margin, ht_data_max + ht_margin
        else:
            ht_margin = ht_range * 0.15  # 15% margin on each side
            ht_min, ht_max = ht_data_min - ht_margin, ht_data_max + ht_margin
    else:
        ht_min, ht_max = -0.5, 0.5  # Default range if no valid delta_ht data
    
    # Align zero points of both y-axes
    # Calculate the position of zero for both axes and adjust ranges accordingly
    def align_zero_points(y1_min, y1_max, y2_min, y2_max):
        """Align zero points of two y-axes by adjusting their ranges proportionally"""
        # Calculate current zero positions (as fraction of total range)
        y1_range = y1_max - y1_min
        y2_range = y2_max - y2_min
        
        if y1_range == 0 or y2_range == 0:
            return y1_min, y1_max, y2_min, y2_max
        
        # Zero position as fraction from bottom
        y1_zero_pos = -y1_min / y1_range
        y2_zero_pos = -y2_min / y2_range
        
        # If both axes include zero, use their natural zero positions
        if y1_min <= 0 <= y1_max and y2_min <= 0 <= y2_max:
            # Find a compromise zero position that doesn't expand ranges too much
            target_zero_pos = (y1_zero_pos + y2_zero_pos) / 2
            
            # Limit extreme adjustments to prevent overly large ranges
            max_expansion = 1.5  # Allow up to 50% range expansion
            
            # Adjust y1 axis
            if target_zero_pos > 0 and target_zero_pos < 1:
                new_y1_below = target_zero_pos * y1_range
                new_y1_above = (1 - target_zero_pos) * y1_range
                
                # Limit expansion
                if new_y1_below / (-y1_min) > max_expansion:
                    new_y1_below = -y1_min * max_expansion
                if new_y1_above / y1_max > max_expansion:
                    new_y1_above = y1_max * max_expansion
                    
                y1_new_min = -new_y1_below
                y1_new_max = new_y1_above
            else:
                y1_new_min, y1_new_max = y1_min, y1_max
            
            # Adjust y2 axis
            if target_zero_pos > 0 and target_zero_pos < 1:
                new_y2_below = target_zero_pos * y2_range
                new_y2_above = (1 - target_zero_pos) * y2_range
                
                # Limit expansion
                if new_y2_below / (-y2_min) > max_expansion:
                    new_y2_below = -y2_min * max_expansion
                if new_y2_above / y2_max > max_expansion:
                    new_y2_above = y2_max * max_expansion
                    
                y2_new_min = -new_y2_below
                y2_new_max = new_y2_above
            else:
                y2_new_min, y2_new_max = y2_min, y2_max
        else:
            # If one or both axes don't include zero, use original ranges
            y1_new_min, y1_new_max = y1_min, y1_max
            y2_new_min, y2_new_max = y2_min, y2_max
        
        return y1_new_min, y1_new_max, y2_new_min, y2_new_max
    
    # Apply zero alignment
    y_min_aligned, y_max_aligned, ht_min_aligned, ht_max_aligned = align_zero_points(y_min, y_max, ht_min, ht_max)
    
    # Create figure with two panels
    fig, axes = plt.subplots(
        1, 2, figsize=(16, 8), gridspec_kw={"width_ratios": [1, 2]}
    )

    # Left panel: Device image
    image_path = load_device_image(target_id)
    if image_path is not None:
        try:
            image = plt.imread(image_path)
            axes[0].imshow(image)
            axes[0].axis("off")
            axes[0].set_title(f"Device Image\n(ID={target_id})", fontsize=12)
        except Exception as e:
            print(f"[WARNING] Failed to load image: {image_path}, error: {e}")
            axes[0].axis("off")
    else:
        axes[0].axis("off")
        axes[0].text(0.5, 0.5, "No Image", ha="center", va="center", fontsize=12)

    # Right panel: Delta_Teq bar chart with delta_ht on second y-axis
    x = np.arange(len(delta_teq_columns))
    width = 0.25  # Width of bars
    
    # Create bars for each temperature condition
    bars_22 = axes[1].bar(x - width, y_22, width=width, label="∆Teq Ta=22°C", color='blue', alpha=0.8)
    bars_25 = axes[1].bar(x, y_25, width=width, label="∆Teq Ta=25°C", color='green', alpha=0.8)
    bars_28 = axes[1].bar(x + width, y_28, width=width, label="∆Teq Ta=28°C", color='orange', alpha=0.8)
    
    # Customize the left y-axis (Delta_Teq)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(body_labels, rotation=45, ha='right')
    axes[1].set_ylabel("∆Teq [°C]", color='black')
    axes[1].set_ylim(y_min_aligned, y_max_aligned)
    axes[1].tick_params(axis='y', labelcolor='black')
    
    # Create second y-axis for delta_ht
    ax2 = axes[1].twinx()
    
    # Plot delta_ht as a single line (regression-based values)
    line_ht = ax2.plot(x, delta_ht_values, 'red', linestyle='--', marker='d', linewidth=2, markersize=4, 
                       label="∆ht (regression)", alpha=0.7)
    
    # Customize the right y-axis (delta_ht)
    ax2.set_ylabel("∆ht [W/m²/°C]", color='red')
    ax2.set_ylim(ht_min_aligned, ht_max_aligned)
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.axhline(y=0, color='red', linestyle=':', alpha=0.5)
    
    # Add title with device information
    title = f"Delta Equivalent Temperature & Heat Transfer Coefficient\n(ID={target_id}, Level={level}"
    if angle is not None:
        title += f", Angle={angle}°"
    title += ")"
    axes[1].set_title(title, fontsize=12)
    
    # Combine legends from both y-axes
    lines1, labels1 = axes[1].get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    axes[1].legend(lines1 + lines2, labels1 + labels2, loc='upper left', bbox_to_anchor=(0, 1))
    
    axes[1].grid(True, alpha=0.3)
    axes[1].axhline(y=0, color='gray', linestyle='--', alpha=0.7)  # Zero line for Delta_Teq
    
    # Adjust layout
    plt.tight_layout()
    
    # Save plot if requested
    if save:
        # Create local_pcs_effects subdirectory if it doesn't exist
        local_effects_dir = os.path.join(Config.FigurePaths.BASE_DIR, "local_pcs_effects")
        os.makedirs(local_effects_dir, exist_ok=True)
        
        filename = f"local_pcs_effects_ID{target_id}.svg"
        save_path = os.path.join(local_effects_dir, filename)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"[SAVED] {save_path}")
    
    plt.close()


def plot_dual_delta_p_with_theoretical_fit(
    df, target_id, body_part, level=None, angle=None, save=False
):
    df_id = df[df[Columns.PCS_ID] == target_id]
    available_levels = df_id[Columns.PCS_Level].dropna().unique().tolist()
    if level is None or level not in available_levels:
        print(
            f"[ERROR] Level '{level}' is not available for ID {target_id}. Available: {available_levels}"
        )
        return
    df_level = df_id[df_id[Columns.PCS_Level] == level]

    if Columns.Angle_Horizontal in df_level.columns:
        available_angles = df_level[Columns.Angle_Horizontal].dropna().unique().tolist()
        if angle is not None:
            if angle not in available_angles:
                print(
                    f"[ERROR] Angle '{angle}' is not available for ID {target_id} and Level {level}. Available: {available_angles}"
                )
                return
            df_level = df_level[df_level[Columns.Angle_Horizontal] == angle]

    if df_level.empty:
        print(f"[ERROR] No data found for ID={target_id}, Level={level}, Angle={angle}")
        return

    delta_p_columns = [col for col in df.columns if col.startswith("Delta_P_")]
    body_labels = [col.replace("Delta_P_", "") for col in delta_p_columns]
    df_22 = extract_data_with_threshold(
        df=df_level, column_name=Columns.PCS_Ta, value=22, threshold=1
    )
    df_25 = extract_data_with_threshold(
        df=df_level, column_name=Columns.PCS_Ta, value=25, threshold=1
    )
    y_22 = df_22[delta_p_columns].mean().values
    y_25 = df_25[delta_p_columns].mean().values
    df_filtered = df_level[df_level[body_part].notna()]
    x_vals = df_filtered[Columns.PCS_Ta].values
    y_vals = df_filtered[body_part].values

    # # Filter out NaN and Inf values
    # valid_indices = (
    #     ~np.isnan(x_vals) & ~np.isnan(y_vals) & ~np.isinf(x_vals) & ~np.isinf(y_vals)
    # )
    # x_vals = x_vals[valid_indices]
    # y_vals = y_vals[valid_indices]

    all_y_values = np.concatenate([y_22, y_25, y_vals])
    all_y_values = all_y_values[~np.isnan(all_y_values)]
    if all_y_values.size == 0:
        print("[ERROR] No valid ∆P data found for selected conditions.")
        return

    y_min, y_max = np.floor(all_y_values.min()), np.ceil(all_y_values.max())
    fig, axes = plt.subplots(
        1, 3, figsize=(18, 6), gridspec_kw={"width_ratios": [1, 2, 2]}
    )

    image_path = load_device_image(target_id)
    if image_path is not None:
        try:
            image = plt.imread(image_path)
            axes[0].imshow(image)
            axes[0].axis("off")
            axes[0].set_title(f"Device Image\n(ID={target_id})", fontsize=12)
        except Exception as e:
            print(f"[WARNING] Failed to load image: {image_path}, error: {e}")
            axes[0].axis("off")
    else:
        axes[0].axis("off")
        axes[0].text(0.5, 0.5, "No Image", ha="center", va="center", fontsize=12)

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

    axes[2].scatter(x_vals, y_vals, color="blue", label="Observed")
    if len(x_vals) > 1:
        m_exp, b_exp = np.polyfit(x_vals, y_vals, 1)
        y_pred_exp = m_exp * x_vals + b_exp
        r2_exp = r2_score(y_vals, y_pred_exp)
        x_fit = np.linspace(20, x_vals.max() + 1, 100)
        y_fit_exp = m_exp * x_fit + b_exp
        axes[2].plot(
            x_fit,
            y_fit_exp,
            "r-",
            label=f"Experimental Fit: P={m_exp:.2f}·Ta{b_exp:+.2f} (R²={r2_exp:.3f})",
        )

        X_theory = x_vals - 34
        hc_theory = np.dot(X_theory, y_vals) / np.dot(X_theory, X_theory)
        y_fit_theory = hc_theory * (x_fit - 34)
        y_pred_theory = hc_theory * (x_vals - 34)
        r2_theory = r2_score(y_vals, y_pred_theory)
        axes[2].plot(
            x_fit,
            y_fit_theory,
            "g--",
            label=f"Theoretical Fit: P={hc_theory:.2f}·(Ta-34) (R²={r2_theory:.3f})",
        )

    axes[2].axvline(x=0, color="black", linestyle=":")
    axes[2].axvline(x=34, color="gray", linestyle="--")

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
        save_path = os.path.join(Config.FigurePaths.BASE_DIR, filename)
        plt.savefig(save_path)
        print(f"[SAVED] {save_path}")
    plt.close()


def main():
    # Use the main PCS database instead of delta_results.csv
    file_path = os.path.join(Config.DataPaths.BASE_DIR, "pcs_database.csv")
    df = pd.read_csv(file_path)

    for target_id in range(1, 18):
        df_id = df[df[Columns.PCS_ID] == target_id]
        available_levels = df_id[Columns.PCS_Level].dropna().unique().tolist()
        if not available_levels:
            print(f"[SKIP] No Level data for ID {target_id}")
            continue
        level = select_default_level(available_levels)

        angle = None
        if Columns.Angle_Horizontal in df_id.columns:
            angle_candidates = (
                df_id[df_id[Columns.PCS_Level] == level][Columns.Angle_Horizontal]
                .dropna()
                .unique()
                .tolist()
            )
            angle = select_default_angle(angle_candidates)

        df_level = df_id[df_id[Columns.PCS_Level] == level]
        if angle is not None:
            df_level = df_level[df_level[Columns.Angle_Horizontal] == angle]
        if df_level.empty:
            continue

        # Check if this device has Delta_Teq data
        delta_teq_columns = [col for col in df.columns if col.startswith("Delta_Teq_")]
        has_teq_data = False
        for col in delta_teq_columns:
            if not df_level[col].isna().all():
                has_teq_data = True
                break
                
        if not has_teq_data:
            print(f"[SKIP] No Delta_Teq data found for ID {target_id}")
            continue

        # Use the new function to plot Delta_Teq with temperature comparison
        plot_local_pcs_effects_with_temperatures(
            df,
            target_id=target_id,
            level=level,
            angle=angle,
            save=True,
        )


if __name__ == "__main__":
    main()
