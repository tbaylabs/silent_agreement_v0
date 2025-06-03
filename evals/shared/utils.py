"""Shared utilities for all evaluation types."""

import os
import shutil
import glob
from datetime import datetime
from typing import Tuple, Optional, List


def setup_directories(model_name: str, eval_type: str, test_mode: Optional[str] = None) -> Tuple[str, str]:
    """
    Set up log and recent result directories for an evaluation run.
    
    Args:
        model_name: Name of the model being evaluated (e.g., "anthropic/claude-3")
        eval_type: Type of evaluation ("base", "reasoning/tokens", "reasoning/effort")
        test_mode: Test mode if any ("quick-test", "test", or None)
    
    Returns:
        Tuple of (model_log_dir, recent_dir) paths
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Convert model name to folder structure
    if model_name.count('/') > 1:
        # Multiple slashes: replace all but the last slash with underscore
        parts = model_name.split('/')
        folder_path = '_'.join(parts[:-1]) + '/' + parts[-1]
    else:
        # Single slash: keep as is
        folder_path = model_name
    
    # Set up log directory for this specific run
    # Use test_results folder for test modes, results folder for full runs
    # Note: 'full' is not a test mode, it should go to results folder
    base_dir = 'data/test_results' if test_mode and test_mode != 'full' else 'data/results'
    model_log_dir = os.path.join(base_dir, eval_type, folder_path, timestamp)
    os.makedirs(model_log_dir, exist_ok=True)
    
    # Clear and recreate recent_result directory
    recent_dir = 'recent_result'
    if os.path.exists(recent_dir):
        shutil.rmtree(recent_dir)
    os.makedirs(recent_dir, exist_ok=True)
    
    return model_log_dir, recent_dir


def display_run_info(eval_type: str, model_name: str, test_mode: Optional[str] = None):
    """Display information about the current evaluation run."""
    print(f"Running {eval_type} for model: {model_name}")
    
    if test_mode:
        print(f"Test mode: {test_mode}")
    else:
        print(f"Full evaluation")


def parse_test_mode(args: List[str]) -> Optional[str]:
    """
    Parse test mode from command line arguments.
    
    Args:
        args: Command line arguments (excluding script name and model name)
    
    Returns:
        Test mode string if found, None otherwise
    """
    for arg in args:
        if arg in ["quick-test", "test"]:
            return arg
        elif arg not in ['--help', '-h', 'help']:  # Allow help flags
            print(f"Unknown argument: {arg}")
            print("Valid test modes: quick-test, test")
            return None
    return None


def copy_results_to_recent(eval_file: str, model_log_dir: str, recent_dir: str, eval_filename: str) -> None:
    """Copy results files to recent_result directory."""
    # Copy the eval file
    recent_eval_path = os.path.join(recent_dir, eval_filename)
    shutil.copy2(eval_file, recent_eval_path)
    print(f"📄 Eval file copied to recent_result: {eval_filename}")
    
    # Copy all result files (different eval types may generate different files)
    result_files = [
        'group_results.json', 
        'options_results.json', 
        'experiment_results.json', 
        'experiment_report.md',
        'token_stats.json'
    ]
    copied_files = []
    for result_file in result_files:
        result_path = os.path.join(model_log_dir, result_file)
        if os.path.exists(result_path):
            shutil.copy2(result_path, os.path.join(recent_dir, result_file))
            copied_files.append(result_file)
    
    if copied_files:
        print(f"📄 Results copied to recent_result: {', '.join(copied_files)}")


def process_eval_results(model_log_dir: str, recent_dir: str, results_processor_func):
    """Process and copy results after evaluation."""
    # Find the eval log file in the model_log_dir
    eval_files = glob.glob(os.path.join(model_log_dir, "*.eval"))
    
    if eval_files:
        eval_file = eval_files[0]  # Should only be one
        eval_filename = os.path.basename(eval_file)
        
        # Generate results using provided processor
        print(f"📊 Generating results...")
        try:
            success = results_processor_func(eval_file, force_overwrite=True)
            
            if success:
                print(f"✅ Results generated in: {model_log_dir}")
                
                # Copy all generated files to recent_result
                copy_results_to_recent(eval_file, model_log_dir, recent_dir, eval_filename)
                
                print(f"\n✅ All files available in: {recent_dir}/")
            else:
                print("⚠️  Results generation failed")
        except Exception as e:
            print(f"⚠️  Error generating results: {e}")
    else:
        print("⚠️  Warning: No .eval file found in log directory")