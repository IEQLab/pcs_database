"""
Data Preprocessing Workflow

This module orchestrates the complete data preprocessing pipeline for PCS Database.
Follows Microsoft enterprise development patterns for maintainability and scalability.

Author: Professional Development Team
"""

import os
import sys
import logging
from typing import List, Dict, Optional
from pathlib import Path

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from code.config.configuration import Config
from code.data_processing.preprocessing import (
    database_columns_names,
    preprocess_manikin,
    preprocess_chamber,
    create_database,
    combine_metadata
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataPreprocessingWorkflow:
    """
    Professional data preprocessing workflow orchestrator.
    
    Handles the complete pipeline from raw data to analysis-ready datasets.
    Implements enterprise-grade error handling, logging, and modularity.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize workflow with configuration."""
        self.config = config or Config()
        self.steps_completed = []
        self.errors_encountered = []
    
    def step1_generate_column_definitions(self) -> bool:
        """Step 1: Generate standardized column definitions."""
        try:
            logger.info("Step 1: Generating column definitions...")
            database_columns_names.main()
            self.steps_completed.append("column_definitions")
            logger.info("✅ Step 1 completed successfully")
            return True
            
        except Exception as e:
            error_msg = f"Step 1 failed: {str(e)}"
            logger.error(error_msg)
            self.errors_encountered.append(error_msg)
            return False
    
    def step2_preprocess_chamber_data(self) -> bool:
        """Step 2: Preprocess environmental chamber data."""
        try:
            logger.info("Step 2: Preprocessing chamber data...")
            preprocess_chamber.main()
            self.steps_completed.append("chamber_preprocessing")
            logger.info("✅ Step 2 completed successfully")
            return True
            
        except Exception as e:
            error_msg = f"Step 2 failed: {str(e)}"
            logger.error(error_msg)
            self.errors_encountered.append(error_msg)
            return False
    
    def step3_preprocess_manikin_data(self) -> bool:
        """Step 3: Preprocess thermal manikin measurement data."""
        try:
            logger.info("Step 3: Preprocessing manikin data...")
            preprocess_manikin.main()
            self.steps_completed.append("manikin_preprocessing")
            logger.info("✅ Step 3 completed successfully")
            return True
            
        except Exception as e:
            error_msg = f"Step 3 failed: {str(e)}"
            logger.error(error_msg)
            self.errors_encountered.append(error_msg)
            return False
    
    def step4_combine_metadata(self) -> bool:
        """Step 4: Combine and standardize metadata."""
        try:
            logger.info("Step 4: Combining metadata...")
            combine_metadata.main()
            self.steps_completed.append("metadata_combination")
            logger.info("✅ Step 4 completed successfully")
            return True
            
        except Exception as e:
            error_msg = f"Step 4 failed: {str(e)}"
            logger.error(error_msg)
            self.errors_encountered.append(error_msg)
            return False
    
    def step5_create_unified_database(self) -> bool:
        """Step 5: Create unified analysis-ready database."""
        try:
            logger.info("Step 5: Creating unified database...")
            create_database.main()
            self.steps_completed.append("database_creation")
            logger.info("✅ Step 5 completed successfully")
            return True
            
        except Exception as e:
            error_msg = f"Step 5 failed: {str(e)}"
            logger.error(error_msg)
            self.errors_encountered.append(error_msg)
            return False
    
    def validate_prerequisites(self) -> bool:
        """Validate that all required directories and files exist."""
        try:
            required_paths = [
                self.config.DataPaths.USYD_DIR,
                self.config.DataPaths.METADATA_DIR,
                self.config.DataPaths.PROCESSED_DATA_DIR
            ]
            
            for path in required_paths:
                if not os.path.exists(path):
                    logger.error(f"Required path does not exist: {path}")
                    return False
            
            logger.info("✅ Prerequisites validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Prerequisites validation failed: {e}")
            return False
    
    def run_full_pipeline(self, validate_first: bool = True) -> bool:
        """
        Execute the complete preprocessing pipeline.
        
        Args:
            validate_first: Whether to validate prerequisites before starting
            
        Returns:
            bool: True if all steps completed successfully
        """
        logger.info("🚀 Starting Data Preprocessing Workflow")
        logger.info("=" * 60)
        
        # Validate prerequisites
        if validate_first and not self.validate_prerequisites():
            logger.error("❌ Prerequisites validation failed. Aborting.")
            return False
        
        # Define processing steps
        steps = [
            ("Column Definitions", self.step1_generate_column_definitions),
            ("Chamber Data Preprocessing", self.step2_preprocess_chamber_data),
            ("Manikin Data Preprocessing", self.step3_preprocess_manikin_data),
            ("Metadata Combination", self.step4_combine_metadata),
            ("Unified Database Creation", self.step5_create_unified_database),
        ]
        
        # Execute steps
        for step_name, step_func in steps:
            logger.info(f"🔄 Executing: {step_name}")
            
            if not step_func():
                logger.error(f"❌ Pipeline failed at: {step_name}")
                self._generate_failure_report()
                return False
        
        # Success
        logger.info("=" * 60)
        logger.info("🎉 Data Preprocessing Pipeline completed successfully!")
        self._generate_success_report()
        return True
    
    def run_partial_pipeline(self, steps: List[str]) -> bool:
        """
        Run only specified steps of the pipeline.
        
        Args:
            steps: List of step names to execute
            Valid steps: ['columns', 'chamber', 'manikin', 'metadata', 'database']
        """
        step_mapping = {
            'columns': self.step1_generate_column_definitions,
            'chamber': self.step2_preprocess_chamber_data,
            'manikin': self.step3_preprocess_manikin_data,
            'metadata': self.step4_combine_metadata,
            'database': self.step5_create_unified_database,
        }
        
        logger.info(f"🔄 Running partial pipeline: {steps}")
        
        for step_name in steps:
            if step_name not in step_mapping:
                logger.error(f"❌ Unknown step: {step_name}")
                return False
            
            logger.info(f"🔄 Executing: {step_name}")
            if not step_mapping[step_name]():
                logger.error(f"❌ Step failed: {step_name}")
                return False
        
        logger.info("✅ Partial pipeline completed successfully!")
        return True
    
    def _generate_success_report(self) -> None:
        """Generate success summary report."""
        report_path = os.path.join(
            self.config.DataPaths.PROCESSED_DATA_DIR, 
            "preprocessing_success_report.txt"
        )
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("DATA PREPROCESSING WORKFLOW - SUCCESS REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Steps completed: {len(self.steps_completed)}\n")
            f.write("Completed steps:\n")
            for step in self.steps_completed:
                f.write(f"  ✅ {step}\n")
            f.write(f"\nReport generated: {report_path}\n")
        
        logger.info(f"📄 Success report saved: {report_path}")
    
    def _generate_failure_report(self) -> None:
        """Generate failure summary report."""
        logger.error("📄 Generating failure report...")
        for error in self.errors_encountered:
            logger.error(f"  ❌ {error}")


def main():
    """Main entry point for preprocessing workflow."""
    import argparse
    
    parser = argparse.ArgumentParser(description="PCS Database Preprocessing Workflow")
    parser.add_argument("--steps", nargs="+", 
                       choices=['columns', 'chamber', 'manikin', 'metadata', 'database'],
                       help="Run specific steps only")
    parser.add_argument("--skip-validation", action="store_true",
                       help="Skip prerequisites validation")
    
    args = parser.parse_args()
    
    # Initialize workflow
    workflow = DataPreprocessingWorkflow()
    
    # Execute workflow
    if args.steps:
        success = workflow.run_partial_pipeline(args.steps)
    else:
        success = workflow.run_full_pipeline(validate_first=not args.skip_validation)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
