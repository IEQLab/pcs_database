"""
This script standardizes product IDs in the raw_data file to ensure that the same products have consistent IDs, 
regardless of their operating conditions (e.g., Fan mode vs. Mist mode). 

The script performs the following tasks:
1. Copies all the raw_data files (e.g. 2025-02-01_ID0_NoPCS_Ta25_TskControl34.csv) and move to a folder called "original"
2. Adds a suffix "_FanMode" to IDs 3, 4, and 10 in raw_data to indicate fan-only operation.
3. Adds a suffix "_MistMode" to IDs 11, 12, and 13 in raw_data, and updates their IDs to 3, 4, and 10, respectively, 
    to match their corresponding fan-only products.
4. Updates all other product IDs according to a predefined mapping (see table below), ensuring unique and consistent IDs.
5. Saves the updated files in raw data folder.

ID mapping example:
     Original_ID    New_ID
     -----------    ------
            1           1
            2           2
            3           3
            4           4
            5           5
            6           6
            7           7
            8           8
            9           9
          10          10
          11           3
          12           4
          13          10
          14          11
          15          12
          16          13
          17          14
          18          15
          19          16
          20          17
"""

import os
import sys
import shutil
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from code.config.configuration import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RawDataRenamer:
    """Professional raw data file renaming utility."""
    
    def __init__(self, raw_data_dir: Optional[str] = None):
        """Initialize the renamer with target directory."""
        self.raw_data_dir = raw_data_dir or os.path.join(
            Config.DataPaths.USYD_DIR, "raw data", "manikin_data"
        )
        self.original_backup_dir = os.path.join(self.raw_data_dir, "original")
        
        # ID mapping as specified in docstring
        self.id_mapping = {
            1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10,
            11: 3, 12: 4, 13: 10, 14: 11, 15: 12, 16: 13, 17: 14, 18: 15, 19: 16, 20: 17
        }
        
        # Special mode mappings
        self.fan_mode_ids = {3, 4, 10}  # Add "_FanMode" suffix
        self.mist_mode_ids = {11, 12, 13}  # Add "_MistMode" suffix and remap ID
    
    def validate_directory(self) -> bool:
        """Validate that the raw data directory exists and contains files."""
        if not os.path.exists(self.raw_data_dir):
            logger.error(f"Raw data directory not found: {self.raw_data_dir}")
            return False
        
        csv_files = list(Path(self.raw_data_dir).glob("*.csv"))
        if not csv_files:
            logger.warning(f"No CSV files found in: {self.raw_data_dir}")
            return False
        
        logger.info(f"Found {len(csv_files)} CSV files in raw data directory")
        return True
    
    def task1_backup_original_files(self) -> bool:
        """Task 1: Create backup of original files in 'original' folder."""
        try:
            # Create backup directory
            os.makedirs(self.original_backup_dir, exist_ok=True)
            
            csv_files = list(Path(self.raw_data_dir).glob("*.csv"))
            backed_up = 0
            
            for file_path in csv_files:
                backup_path = os.path.join(self.original_backup_dir, file_path.name)
                
                if not os.path.exists(backup_path):
                    shutil.copy2(file_path, backup_path)
                    backed_up += 1
                    logger.debug(f"Backed up: {file_path.name}")
            
            logger.info(f"Task 1 completed: {backed_up} files backed up to 'original' folder")
            return True
            
        except Exception as e:
            logger.error(f"Task 1 failed: {e}")
            return False
    
    def parse_filename(self, filename: str) -> Optional[Dict[str, str]]:
        """Parse raw data filename to extract components."""
        # Pattern: 2025-02-01_ID0_NoPCS_Ta25_TskControl34.csv
        pattern = r'^(\d{4}-\d{2}-\d{2})_ID(\d+)_(.+)\.csv$'
        match = re.match(pattern, filename)
        
        if match:
            return {
                'date': match.group(1),
                'original_id': int(match.group(2)),
                'description': match.group(3),
                'extension': '.csv'
            }
        return None
    
    def generate_new_filename(self, parsed: Dict[str, str]) -> str:
        """Generate new standardized filename."""
        original_id = parsed['original_id']
        new_id = self.id_mapping.get(original_id, original_id)
        description = parsed['description']
        
        # Handle special mode suffixes
        if original_id in self.fan_mode_ids:
            # Add FanMode suffix to description
            if "_FanMode" not in description:
                description = f"{description}_FanMode"
        elif original_id in self.mist_mode_ids:
            # Add MistMode suffix and use mapped ID
            if "_MistMode" not in description:
                description = f"{description}_MistMode"
        
        return f"{parsed['date']}_ID{new_id}_{description}{parsed['extension']}"
    
    def task2_add_fan_mode_suffix(self) -> bool:
        """Task 2: Add '_FanMode' suffix to IDs 3, 4, and 10."""
        return self._rename_files_by_condition(
            condition=lambda parsed: parsed['original_id'] in self.fan_mode_ids,
            description="Task 2: Adding FanMode suffix"
        )
    
    def task3_add_mist_mode_suffix_and_remap(self) -> bool:
        """Task 3: Add '_MistMode' suffix to IDs 11, 12, 13 and remap to 3, 4, 10."""
        return self._rename_files_by_condition(
            condition=lambda parsed: parsed['original_id'] in self.mist_mode_ids,
            description="Task 3: Adding MistMode suffix and remapping IDs"
        )
    
    def task4_update_all_other_ids(self) -> bool:
        """Task 4: Update all other product IDs according to mapping."""
        return self._rename_files_by_condition(
            condition=lambda parsed: (
                parsed['original_id'] not in self.fan_mode_ids and 
                parsed['original_id'] not in self.mist_mode_ids and
                parsed['original_id'] in self.id_mapping and
                self.id_mapping[parsed['original_id']] != parsed['original_id']
            ),
            description="Task 4: Updating other product IDs"
        )
    
    def _rename_files_by_condition(self, condition, description: str) -> bool:
        """Rename files that match the given condition."""
        try:
            csv_files = list(Path(self.raw_data_dir).glob("*.csv"))
            renamed_count = 0
            
            for file_path in csv_files:
                # Skip files in backup directory
                if 'original' in str(file_path):
                    continue
                
                parsed = self.parse_filename(file_path.name)
                if not parsed:
                    logger.warning(f"Could not parse filename: {file_path.name}")
                    continue
                
                if condition(parsed):
                    new_filename = self.generate_new_filename(parsed)
                    new_path = file_path.parent / new_filename
                    
                    if file_path != new_path:
                        file_path.rename(new_path)
                        renamed_count += 1
                        logger.debug(f"Renamed: {file_path.name} → {new_filename}")
            
            logger.info(f"{description}: {renamed_count} files renamed")
            return True
            
        except Exception as e:
            logger.error(f"{description} failed: {e}")
            return False
    
    def task5_generate_summary_report(self) -> bool:
        """Task 5: Generate summary report of all changes."""
        try:
            report_path = os.path.join(self.raw_data_dir, "rename_summary_report.txt")
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("RAW DATA FILE RENAME SUMMARY REPORT\n")
                f.write("=" * 50 + "\n\n")
                
                # Current files
                csv_files = list(Path(self.raw_data_dir).glob("*.csv"))
                f.write(f"Current files in directory: {len(csv_files)}\n\n")
                
                # ID mapping table
                f.write("ID MAPPING APPLIED:\n")
                f.write("Original_ID → New_ID\n")
                f.write("-" * 20 + "\n")
                for old_id, new_id in sorted(self.id_mapping.items()):
                    f.write(f"{old_id:11} → {new_id}\n")
                
                f.write(f"\nSpecial Mode Handling:\n")
                f.write(f"FanMode IDs: {sorted(self.fan_mode_ids)}\n")
                f.write(f"MistMode IDs: {sorted(self.mist_mode_ids)}\n")
                
                f.write(f"\nBackup location: {self.original_backup_dir}\n")
            
            logger.info(f"Task 5 completed: Summary report saved to {report_path}")
            return True
            
        except Exception as e:
            logger.error(f"Task 5 failed: {e}")
            return False
    
    def run_all_tasks(self) -> bool:
        """Execute all renaming tasks in sequence."""
        logger.info("Starting comprehensive raw data file renaming...")
        
        if not self.validate_directory():
            return False
        
        tasks = [
            ("Task 1: Backup original files", self.task1_backup_original_files),
            ("Task 2: Add FanMode suffix", self.task2_add_fan_mode_suffix),
            ("Task 3: Add MistMode suffix and remap", self.task3_add_mist_mode_suffix_and_remap),
            ("Task 4: Update other product IDs", self.task4_update_all_other_ids),
            ("Task 5: Generate summary report", self.task5_generate_summary_report),
        ]
        
        for task_name, task_func in tasks:
            logger.info(f"Executing {task_name}...")
            if not task_func():
                logger.error(f"Failed at {task_name}")
                return False
        
        logger.info("All tasks completed successfully!")
        return True


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Rename raw data files according to new ID mapping")
    parser.add_argument("--task", type=int, choices=[1,2,3,4,5], 
                       help="Run specific task only (1-5)")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be renamed without making changes")
    parser.add_argument("--raw-data-dir", type=str,
                       help="Custom raw data directory path")
    
    args = parser.parse_args()
    
    # Initialize renamer
    renamer = RawDataRenamer(args.raw_data_dir)
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No files will be modified")
        # Add dry run logic here if needed
        return
    
    # Execute specific task or all tasks
    if args.task:
        task_map = {
            1: renamer.task1_backup_original_files,
            2: renamer.task2_add_fan_mode_suffix, 
            3: renamer.task3_add_mist_mode_suffix_and_remap,
            4: renamer.task4_update_all_other_ids,
            5: renamer.task5_generate_summary_report
        }
        
        logger.info(f"Running Task {args.task} only...")
        success = task_map[args.task]()
        
    else:
        success = renamer.run_all_tasks()
    
    if success:
        logger.info("Operation completed successfully!")
    else:
        logger.error("Operation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

