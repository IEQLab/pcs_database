# Enhanced PCS Database Interface Design

## Problem Statement

The original PCS database uses numeric level values (0.0, 0.5, 1.0, etc.) which are:
- **Not intuitive** for users who expect "Low", "Mid", "High" terminology
- **Inconsistent** across devices (some have 2 levels, others up to 7)
- **Difficult to remember** specific numeric values for each device

## Solution Design

### 1. User-Friendly Level Mapping

**New Interface:**
```python
# Instead of this (numeric):
device = PCSDatabase.get_device(1, "0.5")

# Users can now do this (intuitive):
device = get_device_simple(1, "Mid")
# or
device = EnhancedPCSDatabase.get_device(1, "Mid")
```

### 2. Intelligent Level Mapping Algorithm

The system automatically maps user-friendly names to numeric levels using smart logic:

**For devices with different level counts:**
- **1 level**: Only "Mid" available
- **2 levels**: "Low" and "High" 
- **3+ levels**: "Low", "Mid", "High"

**Mid-level calculation** leverages the existing `compute_mid_level_effect` utility:
- **Odd number of levels**: Use exact middle level
- **Even number of levels**: Use lower-middle level (more conservative approach)

### 3. Implementation Architecture

```
EnhancedPCSDatabase (new)
├── User-friendly interface (Low/Mid/High)
├── Level mapping logic
├── Backwards compatibility
└── Uses existing PCSDatabase (original)
    ├── Numeric interface (0.0, 0.5, 1.0)
    └── Core data access
```

### 4. Key Features

#### A. Automatic Level Detection
```python
# Get available friendly names for any device
levels = EnhancedPCSDatabase.get_available_level_names(device_id)
# Returns: ['Low', 'Mid', 'High'] or ['Mid'] or ['Low', 'High']
```

#### B. Level Mapping Information
```python
info = EnhancedPCSDatabase.get_level_info(device_id)
# Returns: {
#   'numeric_levels': ['0.0', '0.5', '1.0', '12/12'],
#   'friendly_mapping': {'Low': '0.0', 'Mid': '0.5', 'High': '12/12'},
#   'level_count': 4,
#   ...
# }
```

#### C. Device Comparison
```python
# Compare all devices at the same intuitive level
comparison = compare_all_devices("Mid", max_devices=10)
```

#### D. Backwards Compatibility
```python
# All original numeric methods still work
device1 = PCSDatabase.get_device(1, "0.5")        # Original
device2 = EnhancedPCSDatabase.get_device(1, "0.5") # Enhanced (accepts both)
device3 = EnhancedPCSDatabase.get_device(1, "Mid") # Enhanced (friendly)
```

### 5. Real-World Examples

**Device level mapping examples:**
```
Device 1: ['0.0', '0.5', '1.0', '12/12'] → {'Low': '0.0', 'Mid': '0.5', 'High': '12/12'}
Device 3: ['0.0', '0.33', '0.67', '1.0'] → {'Low': '0.0', 'Mid': '0.33', 'High': '1.0'}
Device 5: ['0.0', '0.25', '0.5', '0.75', '1.0'] → {'Low': '0.0', 'Mid': '0.5', 'High': '1.0'}
Device 7: ['0.0', '0.2', '0.4', '0.6', '0.8', '1.0'] → {'Low': '0.0', 'Mid': '0.4', 'High': '1.0'}
```

### 6. Benefits

#### For Users:
- **Intuitive**: "Mid" is clearer than "0.5"
- **Consistent**: Same terminology across all devices
- **Flexible**: Can still use numeric values if needed

#### For Developers:
- **Backwards compatible**: No breaking changes
- **Extensible**: Easy to add new mapping logic
- **Maintainable**: Leverages existing utilities

#### For Research:
- **Comparable**: Easy to compare devices at equivalent levels
- **Standardized**: Consistent level interpretation across studies
- **Flexible**: Support for both research (numeric) and application (friendly) needs

### 7. Usage Recommendations

**For new code (recommended):**
```python
from code.enhanced_pcsdatabase import get_device_simple, compare_all_devices

# Simple device access
device = get_device_simple(1, "Mid")

# Device comparison
comparison = compare_all_devices("High", max_devices=5)
```

**For existing code:**
- No changes required - all existing code continues to work
- Gradually migrate to friendly interface when convenient

### 8. Integration with Existing Utilities

The enhanced interface integrates seamlessly with your existing `utilities.py`:

- **`compute_mid_level_effect`**: Used internally for intelligent mid-level calculation
- **Temperature filtering**: Works with both interfaces
- **Body part utilities**: Compatible with enhanced device objects

This design provides the best of both worlds: user-friendly interface for everyday use, while maintaining the precision and flexibility of the numeric system for advanced applications.
