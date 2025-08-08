"""
This script visualizes the overall heating/cooling effects of Personal Comfort Systems (PCS) by plotting Delta_Teq values.
Main functionalities:
1. Loads a processed CSV database containing PCS experimental data.
2. Filters and processes data to focus on conditions where ambient air temperature is 25°C, ensuring all PCS conditions are represented.
3. Plots Delta_Teq_All (overall equivalent temperature change) for each PCS_ID:
    - X-axis: Delta_Teq_All (negative values indicate cooling, positive indicate heating)
    - Y-axis: PCS_ID (ordered with PCS_ID=1 at the top)
    - For each PCS_ID, displays the median Delta_Teq_All as a circle, with minimum and maximum values as bars to show the range.
4. Additional plotting of Delta_Teq by body parts for each condition, excluding group-specific columns.
5. Includes utility for selecting a default PCS level from available options, prioritizing numeric or named levels.
Intended usage:
- To provide a clear visual summary of PCS effects across devices and conditions, supporting further analysis and reporting.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import r2_score

# Add the project root directory to sys.path
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

# Add the code directory to sys.path
code_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, code_dir)

from config.configuration import Config
from utils.image_loader import load_device_image


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


def plot_overall_pcs_effects():
    """
    Plot overall PCS effects (Delta_Teq_All) for each PCS_ID at ~25°C ambient temperature.
    """
    # Load the PCS database
    file_path = os.path.join(Config.DataPaths.BASE_DIR, "pcs_database.csv")
    df = pd.read_csv(file_path)
    
    # Filter for ~25°C conditions (24-26°C range)
    df_25c = df[(df['Baseline_Ta'] >= 24) & (df['Baseline_Ta'] <= 26)].copy()
    
    if df_25c.empty:
        print("No data found for ~25°C ambient temperature (24-26°C range)")
        print(f"Available temperatures: {sorted(df['Baseline_Ta'].dropna().unique())}")
        return

    print(f"Found {len(df_25c)} records in 24-26°C range")

    # For each PCS_ID, select default level and calculate statistics
    pcs_stats = []
    
    for pcs_id in sorted(df_25c['PCS_ID'].unique()):
        pcs_data = df_25c[df_25c['PCS_ID'] == pcs_id]
        
        # Select default level using the utility function
        available_levels = pcs_data['PCS_Level'].unique().tolist()
        default_level = select_default_level(available_levels)
        
        # Get data for the default level
        default_data = pcs_data[pcs_data['PCS_Level'] == default_level]
        
        if not default_data.empty:
            delta_teq_all_values = default_data['Delta_Teq_All'].dropna()
            
            if len(delta_teq_all_values) > 0:
                pcs_stats.append({
                    'PCS_ID': pcs_id,
                    'median': delta_teq_all_values.median(),
                    'min': delta_teq_all_values.min(),
                    'max': delta_teq_all_values.max(),
                    'count': len(delta_teq_all_values),
                    'default_level': default_level
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
    ax.set_title('Overall PCS Effects on Equivalent Temperature (~25°C Ambient)\nBlue: Cooling, Red: Heating', fontsize=14)
    
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
