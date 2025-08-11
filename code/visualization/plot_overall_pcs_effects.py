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


def _compute_mid_min_max_from_numeric_levels(df_device: pd.DataFrame) -> dict:
    """
    Given a device DataFrame with numeric PCS_Level (0..1) and Delta_Teq_All, compute:
    - per-level median Delta_Teq_All
    - mid effect: odd -> median at middle level; even -> average of medians at two middle levels
    - min/max across per-level medians
    Returns dict with keys: median, min, max, used_levels, policy.
    """
    # Keep only needed columns
    df = df_device[["PCS_Level", "Delta_Teq_All"]].dropna(subset=["PCS_Level", "Delta_Teq_All"]).copy()
    if df.empty:
        return {}

    # Group by numeric level and compute per-level medians; sort by level value
    level_medians = df.groupby("PCS_Level")["Delta_Teq_All"].median().sort_index()
    if level_medians.empty:
        return {}

    levels = level_medians.index.to_list()
    L = len(levels)

    if L == 1:
        mid_effect = float(level_medians.iloc[0])
    elif L % 2 == 1:
        mid_effect = float(level_medians.iloc[L // 2])
    else:
        mid_effect = float((level_medians.iloc[L // 2 - 1] + level_medians.iloc[L // 2]) / 2.0)

    return {
        "median": mid_effect,
        "min": float(level_medians.min()),
        "max": float(level_medians.max()),
        "used_levels": levels,
        "policy": "mid_level_range",
    }


def _compute_device_stats(df_device: pd.DataFrame) -> dict:
    """Compute per-device mid/min/max using numeric PCS_Level as described above."""
    return _compute_mid_min_max_from_numeric_levels(df_device)


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
    
    # Filter for ~25°C conditions (24-26°C range)
    df_25c = df[(df['Baseline_Ta'] >= 24) & (df['Baseline_Ta'] <= 26)].copy()
    
    if df_25c.empty:
        print("No data found for ~25°C ambient temperature (24-26°C range)")
        print(f"Available temperatures: {sorted(df['Baseline_Ta'].dropna().unique())}")
        return

    print(f"Found {len(df_25c)} records in 24-26°C range")

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
        
        # Plot range as horizontal line
        ax.plot([min_val, max_val], [y_pos, y_pos], 'k-', alpha=0.6, linewidth=2)
        
        # Plot median as circle
        color = 'blue' if median_val < 0 else 'red'
        ax.plot(median_val, y_pos, 'o', color=color, markersize=8, markeredgecolor='black', markeredgewidth=1)
        
        # Plot min/max as vertical bars
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
        Line2D([0], [0], color='black', linewidth=2, label='Min-Max Range')
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
