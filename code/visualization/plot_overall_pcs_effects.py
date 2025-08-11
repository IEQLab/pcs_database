"""
This script visualizes the overall heating/cooling effects of Personal Comfort Systems (PCS) by plotting Delta_Teq values.

Simplified policy (using numeric PCS_Level in [0, 1]):
- For each PCS_ID at ~25°C, compute the median Delta_Teq_All for each unique PCS_Level.
- Choose the "Mid" intensity per device as:
    - If the number of unique levels is odd: pick the middle level (by numeric order) and use its median.
    - If even: take the average of the medians at the two middle levels.
- Plot that Mid effect as the device marker and the min/max of per-level medians as the range bar.

Intended usage:
- Provide a clear and fair per-device summary without complex level heuristics now that PCS_Level is numeric.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Add the project root directory to sys.path
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

# Add the code directory to sys.path
code_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, code_dir)

from config.configuration import Config
from utils.utilities import filter_by_target_temperature, compute_mid_level_effect


def _compute_device_stats(df_device: pd.DataFrame) -> dict:
    """Compute per-device mid/min/max using numeric PCS_Level as described above."""
    return compute_mid_level_effect(df_device, 'Delta_Teq_All')


def plot_overall_pcs_effects():
    """
    Plot overall PCS effects (Delta_Teq_All) for each PCS_ID at ~25°C ambient temperature.

    This uses a fixed policy based on numeric PCS_Level (see module docstring).
    """
    # Load the processed results with numeric PCS_Level
    file_path = os.path.join(
        Config.DataPaths.USYD_DIR, "processed_data", "delta_results.csv"
    )
    df = pd.read_csv(file_path)
    
    # Load device category mapping (Cooling / Heating) from metadata
    try:
        meta_path = os.path.join(Config.DataPaths.METADATA_DIR, "pcs_product_info.csv")
        df_meta = pd.read_csv(meta_path)
        category_map = df_meta.set_index("PCS_ID")["Category"].to_dict()
    except Exception:
        category_map = {}
    
    # Filter for ~25°C conditions using utility function (25°C ± 1°C range)
    df_25c = filter_by_target_temperature(df, target_ta=25.0, tolerance=1.0, ta_column='PCS_Ta')
    
    # For specific PCS_IDs with multiple angles, filter to 270° only
    multi_angle_ids = [8, 9, 10, 13]
    for pid in multi_angle_ids:
        mask = (df_25c['PCS_ID'] == pid)
        if mask.any():
            # Replace with 270° data only, if available
            angle_270_data = df_25c[mask & (df_25c['Angle_Horizontal'] == 270)]
            if len(angle_270_data) > 0:
                # Remove all data for this PCS_ID and add back only 270° data
                df_25c = df_25c[~mask]
                df_25c = pd.concat([df_25c, angle_270_data], ignore_index=True)
            else:
                print(f"Warning: PCS_ID {pid} has no 270° data, using all available angles")
    
    if df_25c.empty:
        print("No data found for target ambient temperature range")
        print(f"Available temperatures: {sorted(df['Baseline_Ta'].dropna().unique())}")
        return

    # Quick validation helper: per-device level medians and mid/min/max comparisons
    def _validate_device(pcs_id: int, df_device: pd.DataFrame):
        sub = df_device[["PCS_Level", "Delta_Teq_All"]].dropna()
        level_medians = sub.groupby("PCS_Level")["Delta_Teq_All"].median().sort_index()
        levels = level_medians.index.to_list()
        vals = level_medians.values.tolist()
        L = len(levels)
        if L == 0:
            return None
        if L == 1:
            mid = float(vals[0])
        elif L % 2 == 1:
            mid = float(vals[L // 2])
        else:
            mid = float((vals[L // 2 - 1] + vals[L // 2]) / 2.0)
        vmin = float(np.min(vals))
        vmax = float(np.max(vals))
        n_points = len(sub)
        level_counts = sub.groupby("PCS_Level").size().to_dict()
        return {
            "PCS_ID": pcs_id,
            "n_levels": L,
            "n_points": n_points,
            "levels": levels,
            "level_medians": vals,
            "mid": round(mid, 3),
            "min": round(vmin, 3),
            "max": round(vmax, 3),
            "mid_is_min": abs(mid - vmin) < 1e-9,
            "mid_is_max": abs(mid - vmax) < 1e-9,
            "level_counts": level_counts,
        }

    # Validate specific IDs of interest and ensure each device has at least 3 unique levels
    to_check = [3, 6, 12, 14]
    print("\nValidation snapshot (IDs: 3, 6, 12, 14):")
    for pid in to_check:
        dev = df_25c[df_25c["PCS_ID"] == pid]
        rep = _validate_device(pid, dev)
        if rep:
            print(rep)
        else:
            print({"PCS_ID": pid, "note": "no data in range"})

    print("\nPer-device checks (n_levels >= 3 recommended):")
    issues = []
    for pid in sorted(df_25c["PCS_ID"].unique()):
        rep = _validate_device(pid, df_25c[df_25c["PCS_ID"] == pid])
        if rep:
            if rep["n_levels"] < 3:
                issues.append((pid, rep["n_levels"]))
    if issues:
        print("Devices with fewer than 3 unique levels:", issues)
    else:
        print("All devices have at least 3 unique levels in this range.")

    # For each PCS_ID, calculate statistics using the selected policy
    pcs_stats = []
    
    for pcs_id in sorted(df_25c['PCS_ID'].unique()):
        pcs_data = df_25c[df_25c['PCS_ID'] == pcs_id]
        stats = _compute_device_stats(pcs_data)
        if stats:
            pcs_stats.append({
                'PCS_ID': pcs_id,
                **stats,
            })
    
    if not pcs_stats:
        print("No valid data found for plotting")
        return
    
    # Convert to DataFrame for easier plotting
    stats_df = pd.DataFrame(pcs_stats)
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot data points
    for _, row in stats_df.iterrows():
        y_pos = row['PCS_ID']
        median_val = row['median']
        min_val = row['min']
        max_val = row['max']
        n_levels = int(row.get('n_levels', 3))
        show_range = bool(row.get('show_range', True))

        # Plot range as horizontal line (only if we have >=2 levels)
        if show_range:
            ax.plot([min_val, max_val], [y_pos, y_pos], 'k-', alpha=0.6, linewidth=2)

        # Plot median as circle colored by corrected Category rule (Cooling=blue, Heating=red)
        # Correct rule: IDs 1–13 => Cooling, IDs >=14 => Heating
        pid = int(row['PCS_ID'])
        category = 'Cooling' if pid <= 13 else 'Heating'
        color = 'blue' if category == 'Cooling' else 'red'
        ax.plot(median_val, y_pos, 'o', color=color, markersize=8, markeredgecolor='black', markeredgewidth=1)

        # Plot endpoint bars
        if show_range:
            if n_levels == 2:
                # For two levels, draw only the Max-end bar if it differs from the Low level
                if not np.isclose(median_val, max_val, atol=1e-9):
                    ax.plot([max_val, max_val], [y_pos-0.15, y_pos+0.15], 'k-', linewidth=2)
            else:
                # For 3+ levels, draw both Min and Max bars
                ax.plot([min_val, min_val], [y_pos-0.15, y_pos+0.15], 'k-', linewidth=2)
                ax.plot([max_val, max_val], [y_pos-0.15, y_pos+0.15], 'k-', linewidth=2)
    
    # Customize the plot
    ax.set_xlabel('Delta_Teq_All (°C)', fontsize=12)
    ax.set_ylabel('PCS_ID', fontsize=12)
    ax.set_title(
        'Overall PCS Effects on Equivalent Temperature (~25°C Ambient)\nMid-level effect with Min/Max per-level range | Blue: Cooling, Red: Heating',
        fontsize=14,
    )
    
    # Set y-axis to show PCS_IDs with ID=1 at the top
    y_ticks = sorted(stats_df['PCS_ID'].unique())
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_ticks)
    # Invert y-axis so that PCS_ID=1 is at the top
    ax.invert_yaxis()
    
    # Add vertical line at x=0
    ax.axvline(x=0, color='gray', linestyle='--', alpha=0.7)
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    # Add legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, 
               markeredgecolor='black', label='Cooling Effect'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=8,
               markeredgecolor='black', label='Heating Effect'),
        Line2D([0], [0], color='black', linewidth=2, label='Min–Max Range (>=2 levels)')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save plots
    figure_dir = Config.FigurePaths.BASE_DIR
    plt.savefig(os.path.join(figure_dir, "overall_pcs_effects.svg"), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(figure_dir, "overall_pcs_effects.png"), dpi=300, bbox_inches='tight')
    
    print(f"Plot saved to {figure_dir}")
    print(f"Plotted {len(stats_df)} PCS devices")
    
    plt.show()

def main():
    """
    Main function to create PCS effect plots.
    """
    print("Creating PCS effects visualizations...")
    
    # Create overall effects plot
    plot_overall_pcs_effects()


if __name__ == "__main__":
    main()
