"""
This script visualizes the overall heating/cooling effects of Personal Comfort Systems (PCS) by plotting Delta_Teq values.
Enhanced version with multi-temperature support (22°C, 25°C, 28°C).

Simplified policy (using numeric PCS_Level in [0, 1]):
- For each PCS_ID at specified temperatures, compute the median Delta_Teq_All for each unique PCS_Level.
- Choose the "Mid" intensity per device as:
    - If the number of unique levels is odd: pick the middle level (by numeric order) and use its median.
    - If even: take the average of the medians at the two middle levels.
- Plot that Mid effect as the device marker and the min/max of per-level medians as the range bar.

Temperature markers:
- 25°C: ○ (circle)
- 22°C: ▲ (triangle)
- 28°C: ■ (square)

Intended usage:
- Provide a clear and fair per-device summary without complex level heuristics now that PCS_Level is numeric.
- Allow comparison across different ambient temperatures.
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


def plot_overall_pcs_effects(show_22c=True, show_28c=True):
    """
    Plot overall PCS effects (Delta_Teq_All) for each PCS_ID at multiple ambient temperatures.
    Optionally include 22°C and 28°C data for comparison.

    Args:
        show_22c (bool): Whether to include 22°C data (triangle markers)
        show_28c (bool): Whether to include 28°C data (square markers)

    This uses a fixed policy based on numeric PCS_Level (see module docstring).
    """
    # Load the processed results with numeric PCS_Level
    file_path = os.path.join(
        Config.DataPaths.BASE_DIR, "pcs_database.csv"
    )
    df = pd.read_csv(file_path)
    
    # Load device category mapping (Cooling / Heating) and names from metadata
    try:
        meta_path = os.path.join(Config.DataPaths.METADATA_DIR, "pcs_product_info.csv")
        df_meta = pd.read_csv(meta_path)
        category_map = df_meta.set_index("PCS_ID")["Category"].to_dict()
        name_map = df_meta.set_index("PCS_ID")["PCS_Name"].to_dict()
    except Exception:
        category_map = {}
        name_map = {}
    
    # Filter data for different temperatures
    df_25c = filter_by_target_temperature(df, target_ta=25.0, tolerance=1.0, ta_column='PCS_Ta')
    
    # Add optional 22°C and 28°C data
    df_22c = None
    df_28c = None
    if show_22c:
        df_22c = filter_by_target_temperature(df, target_ta=22.0, tolerance=1.0, ta_column='PCS_Ta')
    if show_28c:
        df_28c = filter_by_target_temperature(df, target_ta=28.0, tolerance=1.0, ta_column='PCS_Ta')
    
    # Function to apply angle filtering to any temperature dataset
    def apply_angle_filtering(df_temp, temp_name):
        if df_temp is None or df_temp.empty:
            return df_temp
            
        # For specific PCS_IDs with multiple angles, filter to 270° only
        # But be more flexible for dual-mode devices to preserve both Fan and Evaporative data
        multi_angle_ids = [8, 9, 10, 13]
        dual_mode_ids = [3, 4, 10]  # Devices with both Fan and Evaporative modes
        
        for pid in multi_angle_ids:
            mask = (df_temp['PCS_ID'] == pid)
            if mask.any():
                # For dual-mode devices, be more flexible with angle selection
                if pid in dual_mode_ids:
                    # Check if 270° data exists for both modes
                    angle_270_data = df_temp[mask & (df_temp['Angle_Horizontal'] == 270)]
                    fan_270 = angle_270_data[angle_270_data['PCS_Mode'] == 'Fan']
                    evap_270 = angle_270_data[angle_270_data['PCS_Mode'] == 'Evaporative']
                    
                    if len(fan_270) > 0 and len(evap_270) > 0:
                        # Both modes have 270° data, use 270° only
                        df_temp = df_temp[~mask]
                        df_temp = pd.concat([df_temp, angle_270_data], ignore_index=True)
                        print(f"PCS_ID {pid} ({temp_name}): Using 270° data for both modes")
                    else:
                        # At least one mode lacks 270° data, keep all angles
                        print(f"PCS_ID {pid} ({temp_name}): Keeping all angles (some modes lack 270° data)")
                else:
                    # For single-mode devices, apply original logic
                    angle_270_data = df_temp[mask & (df_temp['Angle_Horizontal'] == 270)]
                    if len(angle_270_data) > 0:
                        df_temp = df_temp[~mask]
                        df_temp = pd.concat([df_temp, angle_270_data], ignore_index=True)
                    else:
                        print(f"Warning: PCS_ID {pid} ({temp_name}) has no 270° data, using all available angles")
        return df_temp
    
    # Apply angle filtering to all temperature datasets
    df_25c = apply_angle_filtering(df_25c, "25°C")
    if df_22c is not None:
        df_22c = apply_angle_filtering(df_22c, "22°C")
    if df_28c is not None:
        df_28c = apply_angle_filtering(df_28c, "28°C")
    
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

    # For each PCS_ID, calculate statistics for each available temperature
    # Handle PCS_Mode separately for devices with Fan/Evaporative modes
    pcs_stats = []
    
    # Collect all unique PCS_IDs from all temperature datasets
    all_pcs_ids = set()
    if not df_25c.empty:
        all_pcs_ids.update(df_25c['PCS_ID'].unique())
    if df_22c is not None and not df_22c.empty:
        all_pcs_ids.update(df_22c['PCS_ID'].unique())
    if df_28c is not None and not df_28c.empty:
        all_pcs_ids.update(df_28c['PCS_ID'].unique())
    
    for pcs_id in sorted(all_pcs_ids):
        # Process each temperature dataset
        temp_datasets = [
            (df_25c, '25°C', '○'),
            (df_22c, '22°C', '▲') if show_22c else (None, None, None),
            (df_28c, '28°C', '■') if show_28c else (None, None, None)
        ]
        
        for df_temp, temp_label, marker in temp_datasets:
            if df_temp is None or df_temp.empty:
                continue
                
            pcs_data = df_temp[df_temp['PCS_ID'] == pcs_id]
            if pcs_data.empty:
                continue
            
            # Check if this device has PCS_Mode data (Fan or Evaporative)
            mode_data = pcs_data['PCS_Mode'].dropna()
            unique_modes = mode_data.unique()
            
            if len(unique_modes) > 0 and not all(pd.isna(unique_modes)):
                # Device has PCS_Mode data - split by mode
                for mode in unique_modes:
                    if pd.notna(mode):  # Skip NaN values
                        mode_data_subset = pcs_data[pcs_data['PCS_Mode'] == mode]
                        stats = _compute_device_stats(mode_data_subset)
                        if stats:
                            device_name = name_map.get(pcs_id, f"Device_{pcs_id}")
                            mode_display = "Fan" if mode == "Fan" else "Evaporative"
                            pcs_stats.append({
                                'PCS_ID': pcs_id,
                                'PCS_Mode': mode,
                                'Temperature': temp_label,
                                'Marker': marker,
                                'display_id': f"ID{pcs_id}, {device_name} ({mode_display} mode)",
                                'sort_key': f"{pcs_id:02d}_{mode}_{temp_label}",
                                **stats,
                            })
            else:
                # Device has no PCS_Mode data - use all data as before
                stats = _compute_device_stats(pcs_data)
                if stats:
                    device_name = name_map.get(pcs_id, f"Device_{pcs_id}")
                    pcs_stats.append({
                        'PCS_ID': pcs_id,
                        'PCS_Mode': None,
                        'Temperature': temp_label,
                        'Marker': marker,
                        'display_id': f"ID{pcs_id}, {device_name}",
                        'sort_key': f"{pcs_id:02d}__{temp_label}",
                        **stats,
                    })
    
    # Convert to DataFrame for easier plotting
    if not pcs_stats:
        print("No valid data found for plotting")
        return
    
    stats_df = pd.DataFrame(pcs_stats)
    
    # Create unique device-mode combinations for y-positioning
    # Group by PCS_ID and PCS_Mode to assign the same y-position to different temperatures
    device_mode_combinations = []
    for pcs_id in sorted(stats_df['PCS_ID'].unique()):
        device_data = stats_df[stats_df['PCS_ID'] == pcs_id]
        modes = device_data['PCS_Mode'].unique()
        
        for mode in sorted(modes, key=lambda x: (x is None, x)):  # Sort with None first
            device_name = name_map.get(pcs_id, f"Device_{pcs_id}")
            if pd.notna(mode):
                mode_display = "Fan" if mode == "Fan" else "Evaporative"
                display_id = f"ID{pcs_id}, {device_name} ({mode_display} mode)"
            else:
                display_id = f"ID{pcs_id}, {device_name}"
            
            device_mode_combinations.append({
                'PCS_ID': pcs_id,
                'PCS_Mode': mode,
                'display_id': display_id,
                'y_pos': len(device_mode_combinations)
            })
    
    # Create y-position mapping
    y_pos_map = {}
    for combo in device_mode_combinations:
        key = (combo['PCS_ID'], combo['PCS_Mode'])
        y_pos_map[key] = combo['y_pos']
    
    # Add y_pos to stats_df
    stats_df['y_pos'] = stats_df.apply(
        lambda row: y_pos_map[(row['PCS_ID'], row['PCS_Mode'])], axis=1
    )
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(14, max(8, len(device_mode_combinations) * 0.6)))
    
    # Group data by y_pos (device-mode combination) for plotting
    for y_pos in sorted(stats_df['y_pos'].unique()):
        y_data = stats_df[stats_df['y_pos'] == y_pos]
        
        # Plot each temperature at the same y_pos with slight horizontal offset
        temp_offset = {'25°C': 0, '22°C': -0.1, '28°C': 0.1}  # Small horizontal offsets
        
        for _, row in y_data.iterrows():
            temperature = row['Temperature']
            y_position = y_pos + temp_offset.get(temperature, 0)
            median_val = row['median']
            min_val = row['min']
            max_val = row['max']
            n_levels = int(row.get('n_levels', 3))
            show_range = bool(row.get('show_range', True))
            
            # Plot range as horizontal line (only if we have >=2 levels)
            if show_range:
                ax.plot([min_val, max_val], [y_position, y_position], 'k-', alpha=0.6, linewidth=2)

            # Plot median with appropriate marker and color
            pid = int(row['PCS_ID'])
            category = 'Cooling' if pid <= 10 else 'Heating'
            color = 'blue' if category == 'Cooling' else 'red'
            
            # Select marker based on temperature
            marker_map = {'25°C': 'o', '22°C': '^', '28°C': 's'}
            marker = marker_map.get(temperature, 'o')
            
            ax.plot(median_val, y_position, marker, color=color, markersize=8, 
                    markeredgecolor='black', markeredgewidth=1)

            # Plot endpoint bars
            if show_range:
                if n_levels == 2:
                    # For two levels, draw only the Max-end bar if it differs from the Low level
                    if not np.isclose(median_val, max_val, atol=1e-9):
                        ax.plot([max_val, max_val], [y_position-0.1, y_position+0.1], 'k-', linewidth=2)
                else:
                    # For 3+ levels, draw both Min and Max bars
                    ax.plot([min_val, min_val], [y_position-0.1, y_position+0.1], 'k-', linewidth=2)
                    ax.plot([max_val, max_val], [y_position-0.1, y_position+0.1], 'k-', linewidth=2)
    
    # Customize the plot
    ax.set_xlabel('Delta_Teq_All (°C)', fontsize=12)
    ax.set_ylabel('PCS Device', fontsize=12)
    
    # Create dynamic title based on enabled temperatures
    temp_labels = []
    if show_22c: temp_labels.append('22°C')
    temp_labels.append('25°C')  # Always show 25°C
    if show_28c: temp_labels.append('28°C')
    temp_str = ', '.join(temp_labels)
    
    ax.set_title(
        f'Overall PCS Effects on Equivalent Temperature ({temp_str} Ambient)\n'
        f'Mid-level effect with Min/Max per-level range | Blue: Cooling, Red: Heating',
        fontsize=14,
    )
    
    # Set y-axis to show display IDs
    y_ticks = [combo['y_pos'] for combo in device_mode_combinations]
    y_labels = [combo['display_id'] for combo in device_mode_combinations]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    # Invert y-axis so that lower IDs are at the top
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
    
    # Add temperature-specific legend entries
    if show_22c and show_28c:
        legend_elements.extend([
            Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=8,
                   markeredgecolor='black', label='25°C (○)'),
            Line2D([0], [0], marker='^', color='w', markerfacecolor='gray', markersize=8,
                   markeredgecolor='black', label='22°C (▲)'),
            Line2D([0], [0], marker='s', color='w', markerfacecolor='gray', markersize=8,
                   markeredgecolor='black', label='28°C (■)')
        ])
    elif show_22c:
        legend_elements.extend([
            Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=8,
                   markeredgecolor='black', label='25°C (○)'),
            Line2D([0], [0], marker='^', color='w', markerfacecolor='gray', markersize=8,
                   markeredgecolor='black', label='22°C (▲)')
        ])
    elif show_28c:
        legend_elements.extend([
            Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=8,
                   markeredgecolor='black', label='25°C (○)'),
            Line2D([0], [0], marker='s', color='w', markerfacecolor='gray', markersize=8,
                   markeredgecolor='black', label='28°C (■)')
        ])
    
    ax.legend(handles=legend_elements, loc='upper right')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save plots
    overall_effects_dir = os.path.join(Config.FigurePaths.BASE_DIR, "overall_pcs_effects")
    os.makedirs(overall_effects_dir, exist_ok=True)
    
    svg_path = os.path.join(overall_effects_dir, "TEMP_overall_pcs_effects.svg")
    png_path = os.path.join(overall_effects_dir, "TEMP_overall_pcs_effects.png")
    
    plt.savefig(svg_path, dpi=300, bbox_inches='tight')
    plt.savefig(png_path, dpi=300, bbox_inches='tight')

    print(f"Plot saved to {overall_effects_dir}")
    print(f"SVG: {svg_path}")
    print(f"PNG: {png_path}")
    print(f"Plotted {len(device_mode_combinations)} device combinations")
    
    plt.show()

def main():
    """
    Main function to create PCS effect plots.
    """
    print("Creating PCS effects visualizations with multi-temperature support...")
    
    # Create overall effects plot with all temperatures
    plot_overall_pcs_effects(show_22c=True, show_28c=True)


if __name__ == "__main__":
    main()
