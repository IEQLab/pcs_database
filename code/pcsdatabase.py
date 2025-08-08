"""
PCS Database Access Module

This module provides a simple and efficient way to access PCS (Personal Cooling System) data
from the CSV database using factory functions and data classes.

Architecture:
    - PCSDatabase: Factory class for creating and managing PCS devices
    - PCSDevice: Data model representing individual PCS devices with their properties

Key Features:
    - Factory pattern for safe device creation with validation
    - Caching for improved performance
    - Type-safe property access for all device specifications
    - Integration with thermal calculation functions
    - Comprehensive error handling

Usage Examples:
    Basic device access:
        device = PCSDatabase.get_device(id=1, level="Mid")
        print(f"Brand: {device.brand}")
        print(f"Cooling: {device.cooling_effectiveness:.2f}°C")
    
    Compare power levels:
        devices = PCSDatabase.get_all_levels(id=1)
        for dev in devices:
            print(f"{dev.level}: {dev.power_efficiency:.3f}°C/W")
    
    Calculate thermal effects:
        htc_delta = device.calculate_htc_delta()
        temp_reduction = device.calculate_temperature_reduction()

Design Pattern:
    This follows the Factory + Data Model pattern where:
    - PCSDatabase handles data source management (CSV loading, validation, caching)
    - PCSDevice handles individual device data representation and calculations
    
    This separation provides better testability, maintainability, and follows
    the Single Responsibility Principle.
"""

import os
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

# Try relative imports first (for module execution), then absolute imports (for direct execution)
try:
    from .config.configuration import Config
    from .data_processing.calc_equivalent_temperature import (
        calculate_h_total,
        calculate_delta_h_total,
        calculate_delta_q_skin
    )
except ImportError:
    from config.configuration import Config
    from data_processing.calc_equivalent_temperature import (
        calculate_h_total,
        calculate_delta_h_total,
        calculate_delta_q_skin
    )


class BodyPartDeltaTeq:
    """
    Body part temperature reduction accessor for hierarchical access.
    
    This class provides a clean interface for accessing temperature reduction data
    for different body parts using dot notation: device.delta_teq.head
    
    Examples:
        device.delta_teq.head           # Head cooling
        device.delta_teq.chest          # Chest cooling
        device.delta_teq.left_hand      # Left hand cooling
        device.delta_teq.right_foot     # Right foot cooling
        
        # Get all available parts
        parts = device.delta_teq.available_parts()
        
        # Get all part data as dictionary
        all_data = device.delta_teq.all_parts()
    """
    
    def __init__(self, device_data: pd.Series):
        self._data = device_data
    
    def __getattr__(self, body_part: str) -> float:
        """
        Dynamically access body part temperature reduction.
        
        Args:
            body_part: Body part name (e.g., 'head', 'chest', 'left_hand')
            
        Returns:
            Temperature reduction [°C]
        """
        # Convert to CSV column format (e.g., 'left_hand' -> 'Left_Hand')
        body_part_formatted = '_'.join(word.capitalize() for word in body_part.split('_'))
        column_name = f'Delta_Teq_{body_part_formatted}'
        
        # Return value or 0.0 if not found
        return float(self._data.get(column_name, 0))
    
    def available_parts(self) -> List[str]:
        """
        Get list of available body parts with temperature reduction data.
        
        Returns:
            List of body part names in lowercase with underscores
        """
        delta_columns = [col for col in self._data.index if col.startswith('Delta_Teq_') and col != 'Delta_Teq_All']
        body_parts = []
        
        for col in delta_columns:
            # Extract body part name and convert to lowercase with underscores
            body_part = col[10:]  # Remove 'Delta_Teq_' prefix
            body_part_lower = '_'.join(word.lower() for word in body_part.split('_'))
            body_parts.append(body_part_lower)
        
        return sorted(body_parts)
    
    def all_parts(self) -> Dict[str, float]:
        """
        Get temperature reduction for all available body parts.
        
        Returns:
            Dictionary with body part names as keys and temperature reductions as values
        """
        result = {}
        for body_part in self.available_parts():
            result[body_part] = getattr(self, body_part)
        return result
    
    def major_parts(self) -> Dict[str, float]:
        """
        Get temperature reduction for major body parts (head, chest, back).
        
        Returns:
            Dictionary with major body part names and their temperature reductions
        """
        major_parts = ['head', 'chest', 'back']
        result = {}
        for part in major_parts:
            if part in self.available_parts():
                result[part] = getattr(self, part)
        return result
    
    def __repr__(self) -> str:
        available = len(self.available_parts())
        return f"BodyPartDeltaTeq(available_parts={available})"


@dataclass
class PCSDevice:
    """
    Data model representing a Personal Cooling System device with all thermal and performance data.
    
    This class encapsulates all properties and calculated values for a specific PCS device
    at a particular power level. It provides type-safe access to device specifications,
    environmental conditions, cooling effects, and thermal calculations.
    
    Attributes:
        id: PCS device ID (1-22 for available devices)
        level: Power/intensity level (e.g., "Low", "Mid", "High")
        _data: Raw data row from CSV (private, do not access directly)
    
    Properties:
        Device specs: brand, model_name, type, price_usd, power_consumption
        Environmental: baseline_ta, pcs_ta, baseline_rh, pcs_rh, etc.
        Cooling effects: delta_teq_head, delta_teq_chest, cooling_effectiveness
        Performance: power_efficiency, htc calculations
    
    Examples:
        Basic usage:
            device = PCSDatabase.get_device(id=1, level="Mid")
            print(f"Device: {device.brand} {device.model_name}")
            print(f"Power: {device.power_consumption}W")
            print(f"Cooling: {device.cooling_effectiveness:.2f}°C")
        
        Body part analysis:
            print(f"Head cooling: {device.delta_teq_head:.2f}°C")
            print(f"Chest cooling: {device.delta_teq_chest:.2f}°C")
            print(f"Back cooling: {device.delta_teq_back:.2f}°C")
        
        Performance calculations:
            efficiency = device.power_efficiency
            htc_change = device.calculate_htc_delta()
            temp_reduction = device.calculate_temperature_reduction()
        
        String representation:
            print(device)  # "PCS Device 1 (Mid): Simpeak S20"
            print(repr(device))  # "PCSDevice(id=1, level='Mid', effectiveness=0.15°C)"
    
    Note:
        PCSDevice instances should be created through PCSDatabase.get_device()
        rather than direct instantiation to ensure data validation and caching.
    """
    id: int
    level: str
    _data: pd.Series
    
    # === Device Specifications ===
    @property
    def category(self) -> str:
        """Device category (e.g., 'Cooling')"""
        return self._data.get('Category', '')
    
    @property
    def physical_effect(self) -> str:
        """Physical cooling effect type (e.g., 'Convective', 'Evaporative')"""
        return self._data.get('Physical_Effect', '')
    
    @property
    def type(self) -> str:
        """Device type (e.g., 'Desk fan', 'Evaporative cooler')"""
        return self._data.get('Type', '')
    
    @property
    def brand(self) -> str:
        """Device brand/manufacturer"""
        return self._data.get('Brand', '')
    
    @property
    def model_name(self) -> str:
        """Model name"""
        return self._data.get('Model_Name', '')
    
    @property
    def price_usd(self) -> float:
        """Price in USD"""
        return float(self._data.get('Price_USD', 0))
    
    @property
    def power_consumption(self) -> float:
        """Power consumption in watts"""
        return float(self._data.get('Plug_Power', 0))
    
    # === Baseline Environmental Conditions ===
    @property
    def baseline_ta(self) -> float:
        """Baseline air temperature [°C]"""
        return float(self._data.get('Baseline_Ta', 0))
    
    @property
    def baseline_mrt(self) -> float:
        """Baseline mean radiant temperature [°C]"""
        return float(self._data.get('Baseline_MRT', 0))
    
    @property
    def baseline_rh(self) -> float:
        """Baseline relative humidity [%]"""
        return float(self._data.get('Baseline_RH', 0))
    
    @property
    def baseline_v(self) -> float:
        """Baseline air velocity [m/s]"""
        return float(self._data.get('Baseline_V', 0))
    
    # === PCS Environmental Conditions ===
    @property
    def pcs_ta(self) -> float:
        """Air temperature with PCS [°C]"""
        return float(self._data.get('PCS_Ta', 0))
    
    @property
    def pcs_mrt(self) -> float:
        """Mean radiant temperature with PCS [°C]"""
        return float(self._data.get('PCS_MRT', 0))
    
    @property
    def pcs_rh(self) -> float:
        """Relative humidity with PCS [%]"""
        return float(self._data.get('PCS_RH', 0))
    
    @property
    def pcs_v(self) -> float:
        """Air velocity with PCS [m/s]"""
        return float(self._data.get('PCS_V', 0))
    
    # === Cooling Effects (Delta Equivalent Temperature) ===
    @property
    def delta_teq_all(self) -> float:
        """Overall equivalent temperature reduction [°C]"""
        value = self._data.get('Delta_Teq_All')
        if pd.isna(value):
            # If Delta_Teq_All is not available, calculate average of major body parts
            major_parts = ['Delta_Teq_Head', 'Delta_Teq_Chest', 'Delta_Teq_Back']
            values = [float(self._data.get(part, 0)) for part in major_parts]
            return sum(values) / len(values) if values else 0.0
        return float(value)
    
    @property
    def delta_teq(self) -> BodyPartDeltaTeq:
        """
        Hierarchical access to body part temperature reductions.
        
        This provides a clean interface for accessing temperature reduction data
        for different body parts using dot notation.
        
        Returns:
            BodyPartDeltaTeq instance for accessing individual body parts
            
        Examples:
            # Direct access to specific body parts
            device.delta_teq.head              # Head cooling
            device.delta_teq.chest             # Chest cooling
            device.delta_teq.left_hand         # Left hand cooling
            device.delta_teq.right_foot        # Right foot cooling
            
            # Get available parts and data
            parts = device.delta_teq.available_parts()
            all_data = device.delta_teq.all_parts()
            major_data = device.delta_teq.major_parts()
            
            # Loop access
            for part in ['head', 'chest', 'back']:
                cooling = getattr(device.delta_teq, part)
                print(f"{part}: {cooling:.2f}°C")
        """
        return BodyPartDeltaTeq(self._data)
    
    # === Heat Transfer Data ===
    @property
    def baseline_p_all(self) -> float:
        """Baseline total heat loss [W/m²]"""
        return float(self._data.get('Baseline_P_All', 0))
    
    @property
    def pcs_p_all(self) -> float:
        """Total heat loss with PCS [W/m²]"""
        return float(self._data.get('PCS_P_All', 0))
    
    @property
    def delta_p_all(self) -> float:
        """Change in total heat loss [W/m²]"""
        return float(self._data.get('Delta_P_All', 0))
    
    # === Calculated Properties ===
    @property
    def cooling_effectiveness(self) -> float:
        """Overall cooling effectiveness based on equivalent temperature reduction"""
        return abs(self.delta_teq_all)
    
    @property
    def power_efficiency(self) -> float:
        """Cooling effectiveness per watt [°C/W]"""
        if self.power_consumption > 0:
            return self.cooling_effectiveness / self.power_consumption
        return 0.0
    
    # === Calculation Methods ===
    def calculate_htc_delta(self) -> float:
        """
        Calculate the change in total heat transfer coefficient due to PCS.
        
        Returns:
            Change in heat transfer coefficient [W/m²K]
        """
        try:
            # Calculate baseline heat transfer coefficient
            h_baseline = calculate_h_total(
                q_skin=self.baseline_p_all,
                t_skin=34.0,  # Assumed skin temperature
                t_o=self.baseline_ta  # Using air temperature as approximation
            )
            
            # Calculate PCS heat transfer coefficient
            h_pcs = calculate_h_total(
                q_skin=self.pcs_p_all,
                t_skin=34.0,
                t_o=self.pcs_ta
            )
            
            return calculate_delta_h_total(h_pcs, h_baseline)
        except (ValueError, ZeroDivisionError):
            return 0.0
    
    def calculate_temperature_reduction(self) -> Dict[str, float]:
        """
        Calculate temperature reduction for all body parts.
        
        Returns:
            Dictionary with body part names as keys and temperature reductions as values
        """
        # Get all body part data using the new hierarchical interface
        result = {'overall': self.delta_teq_all, 'effectiveness': self.cooling_effectiveness}
        result.update(self.delta_teq.all_parts())
        return result
    
    def get_body_part_delta(self, body_part: str) -> float:
        """
        Get equivalent temperature reduction for a specific body part.
        
        Args:
            body_part: Body part name (e.g., 'head', 'chest', 'left_hand')
            
        Returns:
            Temperature reduction [°C]
            
        Examples:
            device.get_body_part_delta('head')      # Same as device.delta_teq.head
            device.get_body_part_delta('left_hand') # Same as device.delta_teq.left_hand
        """
        return getattr(self.delta_teq, body_part)
    
    def __str__(self) -> str:
        return f"PCS Device {self.id} ({self.level}): {self.brand} {self.model_name}"
    
    def __repr__(self) -> str:
        return f"PCSDevice(id={self.id}, level='{self.level}', effectiveness={self.cooling_effectiveness:.2f}°C)"


class PCSDatabase:
    """
    Factory class for accessing PCS database with caching, validation, and search capabilities.
    
    This class manages the CSV data source and provides safe, efficient access to PCS devices.
    It implements caching to avoid repeated file reads and comprehensive validation to ensure
    data integrity. All methods are class methods, so no instantiation is required.
    
    Features:
        - Automatic CSV loading and caching
        - Device existence validation before creation
        - Memory-efficient caching of device instances
        - Comprehensive search and filtering capabilities
        - Clear error messages for invalid requests
    
    Class Variables:
        _data: Cached pandas DataFrame of the CSV data
        _cache: Dictionary cache of created PCSDevice instances
    
    Examples:
        Get specific device:
            device = PCSDatabase.get_device(id=1, level="Mid")
            print(f"Effectiveness: {device.cooling_effectiveness:.2f}°C")
        
        Compare all power levels:
            devices = PCSDatabase.get_all_levels(id=1)
            for dev in devices:
                print(f"{dev.level}: {dev.power_efficiency:.3f}°C/W")
        
        Explore available devices:
            ids = PCSDatabase.get_all_device_ids()
            print(f"Available devices: {ids}")
            
            levels = PCSDatabase.get_available_levels(id=1)
            print(f"Device 1 levels: {levels}")
        
        Filter by category:
            cooling_devices = PCSDatabase.filter_by_category("Cooling")
            print(f"Found {len(cooling_devices)} cooling devices")
        
        Error handling:
            try:
                device = PCSDatabase.get_device(id=999, level="Ultra")
            except ValueError as e:
                print(f"Error: {e}")
                # Output: "PCS ID 999 not found in database"
        
        Cache management:
            PCSDatabase.clear_cache()  # Clear memory cache if needed
    
    Note:
        The CSV file path is automatically determined from Config.DataPaths.DATABASE_CSV_FILE.
        The first call to any method will load the CSV data, subsequent calls use cached data.
    """
    
    _data: Optional[pd.DataFrame] = None
    _cache: Dict[tuple, PCSDevice] = {}
    
    @classmethod
    def _load_data(cls) -> pd.DataFrame:
        """Load CSV data if not already loaded."""
        if cls._data is None:
            csv_path = Config.DataPaths.DATABASE_CSV_FILE
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"PCS database CSV not found: {csv_path}")
            cls._data = pd.read_csv(csv_path)
        return cls._data
    
    @classmethod
    def _exists(cls, id: int, level: str) -> bool:
        """Check if a device with given ID and level exists."""
        data = cls._load_data()
        return not data[(data['PCS_ID'] == id) & (data['PCS_Level'] == level)].empty
    
    @classmethod
    def get_device(cls, id: int, level: str) -> PCSDevice:
        """
        Get a PCS device by ID and level.
        
        Args:
            id: PCS device ID (1-20 for Sydney University)
            level: Power level (e.g., "Low", "Mid", "High")
            
        Returns:
            PCSDevice instance
            
        Raises:
            ValueError: If device not found
        """
        # Check cache first
        cache_key = (id, level)
        if cache_key in cls._cache:
            return cls._cache[cache_key]
        
        # Validate existence
        if not cls._exists(id, level):
            available_levels = cls.get_available_levels(id)
            if available_levels:
                raise ValueError(
                    f"PCS ID {id} with level '{level}' not found. "
                    f"Available levels: {available_levels}"
                )
            else:
                raise ValueError(f"PCS ID {id} not found in database")
        
        # Load data
        data = cls._load_data()
        device_data = data[(data['PCS_ID'] == id) & (data['PCS_Level'] == level)].iloc[0]
        
        # Create device and cache
        device = PCSDevice(id=id, level=level, _data=device_data)
        cls._cache[cache_key] = device
        
        return device
    
    @classmethod
    def get_all_levels(cls, id: int) -> List[PCSDevice]:
        """
        Get all available power levels for a specific PCS ID.
        
        Args:
            id: PCS device ID
            
        Returns:
            List of PCSDevice instances for all available levels
        """
        levels = cls.get_available_levels(id)
        return [cls.get_device(id, level) for level in levels]
    
    @classmethod
    def get_available_levels(cls, id: int) -> List[str]:
        """
        Get available power levels for a specific PCS ID.
        
        Args:
            id: PCS device ID
            
        Returns:
            List of available level names
        """
        data = cls._load_data()
        device_data = data[data['PCS_ID'] == id]
        if device_data.empty:
            return []
        return sorted(device_data['PCS_Level'].unique().tolist())
    
    @classmethod
    def get_all_device_ids(cls) -> List[int]:
        """Get all available PCS device IDs."""
        data = cls._load_data()
        return sorted(data['PCS_ID'].unique().tolist())
    
    @classmethod
    def filter_by_category(cls, category: str) -> List[PCSDevice]:
        """
        Filter devices by category.
        
        Args:
            category: Device category (e.g., 'Cooling')
            
        Returns:
            List of matching devices
        """
        data = cls._load_data()
        filtered_data = data[data['Category'] == category]
        
        devices = []
        for _, row in filtered_data.iterrows():
            device = PCSDevice(id=int(row['PCS_ID']), level=row['PCS_Level'], _data=row)
            devices.append(device)
        
        return devices
    
    @classmethod
    def clear_cache(cls):
        """Clear the device cache."""
        cls._cache.clear()


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    try:
        # Get a specific device
        device = PCSDatabase.get_device(id=1, level="Mid")
        print(f"Device: {device}")
        print(f"Brand: {device.brand}")
        print(f"Cooling effectiveness: {device.cooling_effectiveness:.2f}°C")
        print(f"Power efficiency: {device.power_efficiency:.3f}°C/W")
        print(f"Temperature reduction: {device.calculate_temperature_reduction()}")
        
        print("\n" + "="*50)
        
        # Get all levels for device ID 1
        devices = PCSDatabase.get_all_levels(id=1)
        print(f"All levels for PCS ID 1:")
        for dev in devices:
            print(f"  {dev.level}: {dev.cooling_effectiveness:.2f}°C effectiveness")
        
        print("\n" + "="*50)
        
        # Get available device IDs
        ids = PCSDatabase.get_all_device_ids()
        print(f"Available device IDs: {ids}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Test basic functionality when run directly
    print("=== PCS Database Module Test ===")
    try:
        # Test database loading
        device = PCSDatabase.get_device(1, "Mid")
        print(f"Test device: {device.model_name}")
        print(f"Cooling effectiveness: {device.cooling_effectiveness:.2f}°C")
        
        # Test hierarchical body part access
        print("\n=== Hierarchical Body Part Access Test ===")
        print(f"Head cooling: {device.delta_teq.head:.2f}°C")
        print(f"Chest cooling: {device.delta_teq.chest:.2f}°C")
        print(f"Left hand cooling: {device.delta_teq.left_hand:.2f}°C")
        print(f"Right foot cooling: {device.delta_teq.right_foot:.2f}°C")
        
        # Test delta_teq object methods
        print(f"\nDelta teq object: {device.delta_teq}")
        available_parts = device.delta_teq.available_parts()
        print(f"Available body parts: {available_parts[:5]}...")  # Show first 5
        
        # Test all body part deltas
        all_deltas = device.delta_teq.all_parts()
        non_zero_deltas = {k: v for k, v in all_deltas.items() if v != 0}
        print(f"Non-zero cooling effects: {len(non_zero_deltas)} parts")
        
        # Test major parts
        major_parts = device.delta_teq.major_parts()
        print(f"Major parts cooling: {major_parts}")
        
        print("Module test successful!")
    except Exception as e:
        print(f"Module test failed: {e}")
