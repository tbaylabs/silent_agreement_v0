"""
Control data extraction for reusing base evaluation results.
Allows thinking model evaluations to reuse control condition data.
"""

import os
import json
import glob
from pathlib import Path
from typing import List, Dict, Any, NamedTuple, Optional
from inspect_ai.dataset import Sample
from inspect_ai.log import read_eval_log


class BaseEvalInfo(NamedTuple):
    """Information about a base evaluation run."""
    model_name: str
    timestamp: str
    eval_file: str
    sample_count: int
    is_test: bool


class ControlDataExtractor:
    """Extracts and manages control data from base evaluations."""
    
    def __init__(self, data_root: str = "data"):
        self.data_root = Path(data_root)
    
    def discover_base_evals(self, model_name: str, include_test: bool = False) -> List[BaseEvalInfo]:
        """
        Discover available base evaluations for a model.
        
        Args:
            model_name: Name of the model (e.g., "anthropic/claude-3-7-sonnet-20250219")
            include_test: Whether to include test results
            
        Returns:
            List of BaseEvalInfo objects sorted by timestamp (newest first)
        """
        evals = []
        
        # Convert model name to folder structure
        folder_path = self._model_name_to_path(model_name)
        
        # Search both results and test_results
        search_dirs = [self.data_root / "results"]
        if include_test:
            search_dirs.append(self.data_root / "test_results")
        
        for search_dir in search_dirs:
            model_dir = search_dir / folder_path
            if not model_dir.exists():
                continue
            
            # Find all timestamp directories
            for timestamp_dir in model_dir.iterdir():
                if not timestamp_dir.is_dir():
                    continue
                
                # Look for .eval files
                eval_files = list(timestamp_dir.glob("*.eval"))
                if not eval_files:
                    continue
                
                eval_file = eval_files[0]  # Should only be one
                
                # Try to get sample count from eval file
                sample_count = self._get_sample_count(eval_file)
                
                is_test = "test_results" in str(search_dir)
                
                evals.append(BaseEvalInfo(
                    model_name=model_name,
                    timestamp=timestamp_dir.name,
                    eval_file=str(eval_file),
                    sample_count=sample_count,
                    is_test=is_test
                ))
        
        # Sort by timestamp, newest first
        evals.sort(key=lambda x: x.timestamp, reverse=True)
        return evals
    
    def extract_control_samples(self, eval_file: str) -> List[Sample]:
        """
        Extract control condition samples from a base evaluation.
        
        Args:
            eval_file: Path to the .eval file
            
        Returns:
            List of Sample objects for the control condition
        """
        try:
            # Read the eval log
            log = read_eval_log(eval_file)
            
            # Extract samples with control condition
            control_samples = []
            for sample in log.samples:
                if sample.metadata and sample.metadata.get("condition") == "control":
                    control_samples.append(sample)
            
            return control_samples
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract control samples from {eval_file}: {e}")
    
    def validate_control_data(self, samples: List[Sample], expected_count: Optional[int] = None) -> bool:
        """
        Validate extracted control data.
        
        Args:
            samples: List of control samples
            expected_count: Optional expected number of samples
            
        Returns:
            True if validation passes
            
        Raises:
            RuntimeError: If validation fails
        """
        if not samples:
            raise RuntimeError("No control samples found")
        
        # Check that all samples have the required metadata
        for i, sample in enumerate(samples):
            if not sample.metadata:
                raise RuntimeError(f"Sample {i} missing metadata")
            
            if sample.metadata.get("condition") != "control":
                raise RuntimeError(f"Sample {i} not a control condition: {sample.metadata.get('condition')}")
            
            required_fields = ["option_id", "condition"]
            for field in required_fields:
                if field not in sample.metadata:
                    raise RuntimeError(f"Sample {i} missing required metadata field: {field}")
        
        # Check expected count if provided
        if expected_count is not None and len(samples) != expected_count:
            raise RuntimeError(
                f"Expected {expected_count} control samples, got {len(samples)}"
            )
        
        return True
    
    def interactive_select_base_eval(self, model_name: str, include_test: bool = False) -> Optional[BaseEvalInfo]:
        """
        Interactively select a base evaluation.
        
        Args:
            model_name: Name of the model
            include_test: Whether to include test results
            
        Returns:
            Selected BaseEvalInfo or None if cancelled
        """
        evals = self.discover_base_evals(model_name, include_test)
        
        if not evals:
            print(f"No base evaluations found for model: {model_name}")
            if not include_test:
                print("Try including test results with include_test=True")
            return None
        
        print(f"\\nAvailable base evaluations for {model_name}:")
        print(f"{'#':<3} {'Timestamp':<15} {'Samples':<8} {'Type':<8} {'File'}")
        print("-" * 70)
        
        for i, eval_info in enumerate(evals):
            eval_type = "test" if eval_info.is_test else "full"
            filename = Path(eval_info.eval_file).name
            print(f"{i+1:<3} {eval_info.timestamp:<15} {eval_info.sample_count:<8} {eval_type:<8} {filename}")
        
        while True:
            try:
                choice = input(f"\\nSelect evaluation (1-{len(evals)}, or 'q' to quit): ").strip()
                if choice.lower() == 'q':
                    return None
                
                index = int(choice) - 1
                if 0 <= index < len(evals):
                    return evals[index]
                else:
                    print(f"Invalid choice. Please enter 1-{len(evals)}")
            
            except (ValueError, KeyboardInterrupt):
                print("Invalid input. Please enter a number or 'q'")
    
    def _model_name_to_path(self, model_name: str) -> str:
        """Convert model name to directory path structure."""
        if model_name.count('/') > 1:
            # Multiple slashes: replace all but the last slash with underscore
            parts = model_name.split('/')
            return '_'.join(parts[:-1]) + '/' + parts[-1]
        else:
            # Single slash: keep as is
            return model_name
    
    def _get_sample_count(self, eval_file: Path) -> int:
        """Get sample count from eval file."""
        try:
            log = read_eval_log(str(eval_file))
            return len(log.samples)
        except:
            return 0  # Return 0 if can't read