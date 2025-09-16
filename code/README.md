# Code Directory

This directory contains the Python modules for this project.

## Main Code

### `pcsdatabase.py` - Primary Database Code

The main module providing access to this database with factory pattern and data classes. See more details in the example code.

**Key Classes:**

- `PCSDatabase` - Factory class for creating and managing PCS devices
- `PCSDevice` - Data model representing individual devices with thermal properties

**Usage Examples:**

```python
# Get device at different power levels
device_low = PCSDatabase.get_device(id=1, level="Low")
device_mid = PCSDatabase.get_device(id=1, level="Mid")
device_high = PCSDatabase.get_device(id=1, level="High")
```

## Directory Structure

### Configuration (`config/`)

- `configuration.py` - File paths, database settings, project configuration
- `columns.py` - Database column definitions and naming conventions
- `manikin_body_part_names.py` - Standardized body part naming system

### Data Processing (`data_processing/`)

**Subdirectories:**

- `analysis/` - For analysis and calculation
- `preprocessing/` - Preprocess code for the raw data
- `compilation/` - Data compilation workflows
- `validation/` - Data quality checks and validation

### Visualization (`visualization/`)

For visualization. Please see the file names.

### Utilities (`utils/`)

- `utilities.py` - Main utility code that includes common utility functions and helpers
- For other utility code, please see the other file names.

### Workflows (`workflows/`)

- `preprocess_workflow.py` - Complete end-to-end data processing pipeline

### [Not included in Git] Development Tools (`debug/`)

Debug scripts for data validation and troubleshooting:
