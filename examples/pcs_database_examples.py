"""
PCS Database Examples - Demonstrating Both Traditional and Friendly Level Interfaces

This script shows how to use the PCS database with both:
1. Traditional numeric levels (backwards compatible)
2. New friendly level names (Low/Mid/High) 

The friendly interface intelligently maps to actual device levels using
the compute_mid_level_effect algorithm for consistent Mid-level selection.
"""

import sys
import os

# Add project root to Python path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from code.pcsdatabase import PCSDatabase

def main():
    print("=" * 60)
    print("PCS Database Examples - Traditional and Friendly Interfaces")
    print("=" * 60)
    
    # === Example 1: Traditional numeric interface (backwards compatible) ===
    print("\n=== Example 1: Traditional Numeric Interface ===")
    try:
        device = PCSDatabase.get_device(id=1, level="0.5")
        print(f"Device: {device.brand} {device.model_name}")
        print(f"Level: {device.level}")
        print(f"Overall cooling: {device.delta_teq_all:.2f}°C")
        print(f"Head cooling: {device.delta_teq.head:.2f}°C")
        print(f"Power efficiency: {device.power_efficiency:.3f}°C/W")
    except Exception as e:
        print(f"Error: {e}")
    
    # === Example 2: New friendly level interface ===
    print("\n=== Example 2: Friendly Level Interface ===")
    try:
        # Test all friendly levels for Device 1
        for level_name in ["Low", "Mid", "High"]:
            device = PCSDatabase.get_device(id=1, level=level_name)
            actual_level = PCSDatabase._normalize_level(1, level_name)
            print(f"{level_name:4} level: {device.cooling_effectiveness:.2f}°C (actual: {actual_level})")
    except Exception as e:
        print(f"Error: {e}")
    
    # === Example 3: Level mapping information ===
    print("\n=== Example 3: Level Mapping Information ===")
    try:
        level_info = PCSDatabase.get_level_info(1)
        print("Device 1 level mapping:")
        for friendly, actual in level_info['friendly_mapping'].items():
            print(f"  {friendly}: {actual}")
        print(f"Total available levels: {level_info['total_levels']}")
        print(f"All levels: {level_info['available_levels']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # === Example 4: Device comparison at same friendly level ===
    print("\n=== Example 4: Device Comparison at Mid Level ===")
    try:
        devices = [1, 2, 3, 4, 5]
        comparison = PCSDatabase.compare_devices_by_effectiveness(devices, level="Mid")
        print("Top 5 devices at Mid level (by effectiveness):")
        for i, dev in enumerate(comparison, 1):
            print(f"  {i}. Device {dev['id']} ({dev['brand']}): {dev['effectiveness']:.2f}°C")
            print(f"      Power: {dev['power_consumption']:.1f}W, Efficiency: {dev['power_efficiency']:.3f}°C/W")
    except Exception as e:
        print(f"Error: {e}")
    
    # === Example 5: Cross-level analysis for one device ===
    print("\n=== Example 5: Cross-Level Analysis - Device 8 ===")
    try:
        device_id = 8
        level_info = PCSDatabase.get_level_info(device_id)
        print(f"Device {device_id} available levels: {level_info['available_levels']}")
        print(f"Friendly mapping: {level_info['friendly_mapping']}")
        
        print("\nPerformance across levels:")
        for friendly_level in ["Low", "Mid", "High"]:
            try:
                device = PCSDatabase.get_device(device_id, friendly_level)
                actual_level = PCSDatabase._normalize_level(device_id, friendly_level)
                print(f"  {friendly_level:4} ({actual_level:4}): {device.cooling_effectiveness:.2f}°C, "
                      f"{device.power_consumption:.1f}W, {device.power_efficiency:.3f}°C/W")
            except ValueError:
                print(f"  {friendly_level:4}: Not available")
    except Exception as e:
        print(f"Error: {e}")
    
    # === Example 6: Body part analysis with friendly levels ===
    print("\n=== Example 6: Body Part Analysis - Device 1 at High Level ===")
    try:
        device = PCSDatabase.get_device(id=1, level="High")
        print(f"Device: {device.brand} {device.model_name} at High level")
        print(f"Actual level: {PCSDatabase._normalize_level(1, 'High')}")
        
        # Major body parts
        major_parts = device.delta_teq.major_parts()
        print("Major body part cooling:")
        for part, cooling in major_parts.items():
            print(f"  {part.capitalize()}: {cooling:.2f}°C")
        
        # Overall effectiveness
        print(f"Overall effectiveness: {device.cooling_effectiveness:.2f}°C")
    except Exception as e:
        print(f"Error: {e}")
    
    # === Example 7: Error handling demonstration ===
    print("\n=== Example 7: Error Handling ===")
    try:
        # Try invalid device ID
        device = PCSDatabase.get_device(id=999, level="Mid")
    except ValueError as e:
        print(f"Expected error for invalid device: {e}")
    
    try:
        # Try invalid level for valid device
        device = PCSDatabase.get_device(id=1, level="Ultra")
    except ValueError as e:
        print(f"Expected error for invalid level: {e}")

if __name__ == "__main__":
    main()
