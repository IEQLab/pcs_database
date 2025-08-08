"""
Simple usage examples for PCS Database Access Module
"""

from code.pcsdatabase import PCSDatabase

def main():
    print("=== PCS Database Access Examples ===\n")
    
    # Example 1: Get specific device
    print("1. Getting specific device (ID=1, Level=Mid):")
    device = PCSDatabase.get_device(id=1, level="Mid")
    print(f"Device: {device.brand} {device.model_name}")
    print(f"Cooling effectiveness: {device.cooling_effectiveness:.2f}°C")
    print(f"Power consumption: {device.power_consumption}W")
    print(f"Power efficiency: {device.power_efficiency:.3f}°C/W")
    print(f"Head cooling: {device.delta_teq_head:.2f}°C")
    print(f"Chest cooling: {device.delta_teq_chest:.2f}°C")

    print("\n" + "-"*50)
    
    # Example 2: Compare all levels of same device
    print("\n2. Comparing all power levels for Device ID 1:")
    devices = PCSDatabase.get_all_levels(id=1)
    for dev in devices:
        print(f"   {dev.level:>4}: {dev.cooling_effectiveness:.2f}°C "
              f"({dev.power_efficiency:.3f}°C/W)")
    
    print("\n" + "-"*50)
    
    # Example 3: Find most efficient device
    print("\n3. Finding most efficient devices:")
    all_ids = PCSDatabase.get_all_device_ids()[:5]  # First 5 devices
    
    best_effectiveness = 0
    best_efficiency = 0
    best_device_eff = None
    best_device_power = None
    
    for device_id in all_ids:
        try:
            levels = PCSDatabase.get_available_levels(device_id)
            for level in levels:
                device = PCSDatabase.get_device(device_id, level)
                
                if device.cooling_effectiveness > best_effectiveness:
                    best_effectiveness = device.cooling_effectiveness
                    best_device_eff = device
                
                if device.power_efficiency > best_efficiency:
                    best_efficiency = device.power_efficiency
                    best_device_power = device
        except Exception as e:
            print(f"   Skipping device {device_id}: {e}")
    
    if best_device_eff:
        print(f"   Most effective: ID {best_device_eff.id} ({best_device_eff.level}) - "
              f"{best_device_eff.cooling_effectiveness:.2f}°C")
    
    if best_device_power:
        print(f"   Most efficient: ID {best_device_power.id} ({best_device_power.level}) - "
              f"{best_device_power.power_efficiency:.3f}°C/W")
    
    print("\n" + "-"*50)
    
    # Example 4: Calculate HTC delta
    print("\n4. Heat Transfer Coefficient calculation:")
    device = PCSDatabase.get_device(id=1, level="High")
    htc_delta = device.calculate_htc_delta()
    print(f"   Device: {device}")
    print(f"   HTC Delta: {htc_delta:.3f} W/m²K")
    
    print("\n" + "-"*50)
    
    # Example 5: Error handling
    print("\n5. Error handling examples:")
    try:
        invalid_device = PCSDatabase.get_device(id=999, level="Ultra")
    except ValueError as e:
        print(f"   Expected error: {e}")
    
    try:
        invalid_level = PCSDatabase.get_device(id=1, level="Invalid")
    except ValueError as e:
        print(f"   Expected error: {e}")

if __name__ == "__main__":
    main()
