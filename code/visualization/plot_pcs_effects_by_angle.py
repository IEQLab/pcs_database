"""
This code generates graphs to compare the effects of Personal Cooling Systems (PCS) at different angles.
The target PCS IDs are 8, 9, 10, and 13, which correspond to standing fans or evaporative cooling devices.

The angles compared are 180°, 225°, and 270°.

Data is extracted from the database under the condition that ambient temperature (Ta) is 25°C or lower.

The x-axis of the graph represents body parts (whole body, head, chest, etc.), and the y-axis shows the equivalent temperature for each part.
Data for each angle is plotted using different lines and markers.

Notes:
- The database is filtered by PCS ID, angle, and ambient temperature condition.
- For each PCS and angle combination, the equivalent temperature for each body part is calculated and retrieved.
- The graph overlays multiple lines (one for each angle) to visually compare the effects of PCS.
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


def plot_pcs_effects_by_angle(target_pcs_ids=[8, 9, 10, 13], target_angles=[180, 225, 270], target_ta=25.0, tolerance=1.0):
    """
    Plot PCS effects by angle for standing fans and evaporative coolers.
    
    Args:
        target_pcs_ids: List of PCS_IDs to analyze (default: [8, 9, 10, 13])
        target_angles: List of angles to compare (default: [180, 225, 270])
        target_ta: Target ambient temperature in °C (default: 25.0)
        tolerance: Temperature tolerance in °C (default: 1.0)
    """
    # Load the processed results
    file_path = os.path.join(
        Config.DataPaths.USYD_DIR, "processed_data", "delta_results.csv"
    )
    df = pd.read_csv(file_path)
    
    # Filter by temperature condition using utility function
    df_filtered = filter_by_target_temperature(df, target_ta=target_ta, tolerance=tolerance, ta_column='PCS_Ta')
    
    # Filter by target PCS IDs
    df_filtered = df_filtered[df_filtered['PCS_ID'].isin(target_pcs_ids)]
    
    print(f"Found {len(df_filtered)} records for PCS IDs {target_pcs_ids} at {target_ta}°C ± {tolerance}°C")
    
    # Check available body part columns in the data
    available_body_parts = []
    for col in df_filtered.columns:
        if col.startswith('Delta_Teq_') and col != 'Delta_Teq_All':
            body_part = col.replace('Delta_Teq_', '')
            available_body_parts.append(body_part)
    
    print(f"Available body parts in data: {available_body_parts[:10]}")  # Show first 10
    
    # Use available body parts instead of predefined list
    main_body_parts = available_body_parts if available_body_parts else ['head', 'chest', 'back', 'pelvis', 
                       'left_upper_arm', 'right_upper_arm', 
                       'left_thigh', 'right_thigh']
    
    # Create subplots for each PCS
    n_pcs = len(target_pcs_ids)
    fig, axes = plt.subplots(2, 2, figsize=(20, 14))
    axes = axes.flatten()
    
    # Color and marker styles for different angles
    angle_styles = {
        180: {'color': 'blue', 'marker': 'o', 'linestyle': '-', 'label': '180°'},
        225: {'color': 'red', 'marker': 's', 'linestyle': '--', 'label': '225°'},
        270: {'color': 'green', 'marker': '^', 'linestyle': '-.', 'label': '270°'}
    }
    
    for i, pcs_id in enumerate(target_pcs_ids):
        ax = axes[i]
        pcs_data = df_filtered[df_filtered['PCS_ID'] == pcs_id]
        
        if pcs_data.empty:
            ax.text(0.5, 0.5, f'No data for PCS {pcs_id}', 
                   transform=ax.transAxes, ha='center', va='center')
            ax.set_title(f'PCS {pcs_id} - No Data')
            continue
        
        # For each angle, calculate mid-level effects for body parts
        angle_data = {}
        for angle in target_angles:
            angle_subset = pcs_data[pcs_data['Angle_Horizontal'] == angle]
            if not angle_subset.empty:
                # Calculate mid-level effect for each body part using utility function
                body_part_effects = []
                body_part_labels = []
                
                # Add whole body first
                if 'Delta_Teq_All' in angle_subset.columns:
                    whole_body_stats = compute_mid_level_effect(angle_subset, 'Delta_Teq_All')
                    if whole_body_stats:
                        body_part_effects.append(whole_body_stats['median'])
                        body_part_labels.append('Whole Body')
                
                # Add individual body parts
                for part in main_body_parts:
                    delta_col = f'Delta_Teq_{part}'
                    if delta_col in angle_subset.columns and not angle_subset[delta_col].isna().all():
                        part_stats = compute_mid_level_effect(angle_subset, delta_col)
                        if part_stats:
                            body_part_effects.append(part_stats['median'])
                            body_part_labels.append(part.replace('_', ' ').title())
                
                angle_data[angle] = {
                    'effects': body_part_effects,
                    'labels': body_part_labels,
                    'n_points': len(angle_subset)
                }
        
        # Plot lines for each angle
        if angle_data:
            # Use the first angle's labels as x-axis (assuming all angles have same body parts)
            first_angle = list(angle_data.keys())[0]
            x_labels = angle_data[first_angle]['labels']
            x_positions = range(len(x_labels))
            
            for angle in target_angles:
                if angle in angle_data:
                    style = angle_styles[angle]
                    effects = angle_data[angle]['effects']
                    n_points = angle_data[angle]['n_points']
                    
                    ax.plot(x_positions, effects, 
                           color=style['color'], 
                           marker=style['marker'],
                           linestyle=style['linestyle'],
                           linewidth=2,
                           markersize=6,
                           label=f"{style['label']} (n={n_points})")
            
            # Customize subplot
            ax.set_title(f'PCS {pcs_id} - Mid-Level Effects by Angle', fontsize=14, fontweight='bold')
            ax.set_xlabel('Body Parts', fontsize=12)
            ax.set_ylabel('Delta Teq (°C) - Mid Level', fontsize=12)
            ax.set_xticks(x_positions)
            ax.set_xticklabels(x_labels, rotation=30, ha='right', fontsize=10)
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=10)
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=0.8)
        else:
            ax.text(0.5, 0.5, f'No valid angle data\nfor PCS {pcs_id}', 
                   transform=ax.transAxes, ha='center', va='center')
            ax.set_title(f'PCS {pcs_id} - No Valid Data')
    
    # Overall plot settings
    plt.suptitle(f'PCS Mid-Level Effects by Angle Comparison ({target_ta}°C ± {tolerance}°C)', 
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Save plots
    figure_dir = Config.FigurePaths.BASE_DIR
    output_path = os.path.join(figure_dir, "pcs_effects_by_angle")
    plt.savefig(f"{output_path}.svg", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_path}.png", dpi=300, bbox_inches='tight')
    
    print(f"PCS effects by angle plots saved to {figure_dir}")
    
    # Print summary statistics
    print("\nDetailed data summary:")
    print("="*50)
    for pcs_id in target_pcs_ids:
        pcs_data = df_filtered[df_filtered['PCS_ID'] == pcs_id]
        if not pcs_data.empty:
            print(f"\nPCS {pcs_id}:")
            angle_counts = pcs_data['Angle_Horizontal'].value_counts().sort_index()
            print(f"  Angle distribution: {dict(angle_counts)}")
            
            # Check PCS_Level distribution for each angle and show mid-level calculation
            for angle in target_angles:
                angle_data = pcs_data[pcs_data['Angle_Horizontal'] == angle]
                if not angle_data.empty:
                    level_counts = angle_data['PCS_Level'].value_counts().sort_index()
                    ta_range = f"{angle_data['PCS_Ta'].min():.1f}-{angle_data['PCS_Ta'].max():.1f}°C"
                    
                    # Calculate mid-level for whole body to show the calculation
                    whole_body_stats = compute_mid_level_effect(angle_data, 'Delta_Teq_All')
                    mid_value = whole_body_stats.get('median', 'N/A') if whole_body_stats else 'N/A'
                    n_levels = whole_body_stats.get('n_levels', 0) if whole_body_stats else 0
                    
                    print(f"    {angle}°: {len(angle_data)} records, PCS_Level: {dict(level_counts)}, Ta: {ta_range}")
                    print(f"      → Mid-level whole body effect: {mid_value:.3f}°C (from {n_levels} levels)")
            
            # Show example body part data availability
            sample_record = pcs_data.iloc[0]
            available_parts = []
            for part in ['All'] + main_body_parts[:5]:  # Show first 5 body parts
                col_name = f'Delta_Teq_{part}' if part != 'All' else 'Delta_Teq_All'
                if col_name in sample_record.index and pd.notna(sample_record[col_name]):
                    available_parts.append(part)
            print(f"  Available body parts: {available_parts}")
        else:
            print(f"PCS {pcs_id}: No data")
    print("="*50)
    
    plt.show()


def main():
    """
    Main function to create PCS effects by angle comparison plots.
    """
    print("Creating PCS effects by angle comparison...")
    plot_pcs_effects_by_angle()


if __name__ == "__main__":
    main()