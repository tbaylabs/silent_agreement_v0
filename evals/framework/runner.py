"""
Generic evaluation runner framework.
Handles common evaluation workflow patterns.
"""

import os
import sys
import shutil
import glob
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from inspect_ai import eval
from typing import Dict, Any, List

from evals.framework.config import EvalConfig


class EvalRunner:
    """Generic evaluation runner that handles common workflow patterns."""
    
    def __init__(self, config: EvalConfig):
        self.config = config
        
    def run(self, model_name: str, args: List[str]) -> None:
        """
        Run the evaluation with the given model and arguments.
        
        Args:
            model_name: Name of the model to evaluate
            args: Command line arguments
        """
        # Load environment variables
        self._load_environment()
        
        # Parse arguments using config
        parsed_args = self.config.parse_args(args)
        
        # Validate setup
        self.config.validate_setup(parsed_args)
        
        # Set up directories
        model_log_dir, recent_dir = self._setup_directories(model_name, parsed_args)
        
        # Display run information
        self._display_run_info(model_name, parsed_args)
        
        try:
            # Get task factory and parameters
            task_factory = self.config.get_task_factory()
            eval_params = self.config.get_eval_params(parsed_args)
            
            # Get model-specific parameters if config supports it
            additional_params = {}
            if hasattr(self.config, 'get_model_specific_params'):
                additional_params = self.config.get_model_specific_params(model_name)
            
            # Run the evaluation
            eval_kwargs = {
                "model": model_name,
                "log_dir": model_log_dir,
                **additional_params
            }
            
            logs = eval(task_factory(**eval_params), **eval_kwargs)
            log = logs[0]  # Get the first (and only) log
            
            if log.status == "success":
                print(f"✅ Evaluation completed successfully!")
                
                # Process results
                self._process_results(model_log_dir, recent_dir, parsed_args)
                
            else:
                print(f"❌ Evaluation failed with status: {log.status}")
                if hasattr(log, 'error') and log.error:
                    print(f"Error: {log.error}")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Error running evaluation: {str(e)}")
            sys.exit(1)
    
    def _load_environment(self) -> None:
        """Load environment variables from .env file."""
        env_file = find_dotenv()
        if env_file:
            print(f"Loading environment from: {env_file}")
            load_dotenv(env_file)
        else:
            print("No .env file found - API keys may not be available")
    
    def _setup_directories(self, model_name: str, parsed_args: Dict[str, Any]) -> tuple:
        """
        Set up log and recent result directories.
        
        Returns:
            Tuple of (model_log_dir, recent_dir)
        """
        # Create timestamp for this run
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
        test_mode = parsed_args.get("test_mode")
        base_dir = 'data/test_results' if test_mode else 'data/results'
        model_log_dir = os.path.join(base_dir, folder_path, timestamp)
        os.makedirs(model_log_dir, exist_ok=True)
        
        # Clear and recreate recent_result directory
        recent_dir = 'recent_result'
        if os.path.exists(recent_dir):
            shutil.rmtree(recent_dir)
        os.makedirs(recent_dir, exist_ok=True)
        
        return model_log_dir, recent_dir
    
    def _display_run_info(self, model_name: str, parsed_args: Dict[str, Any]) -> None:
        """Display information about the current run."""
        print(f"Running {self.config.get_name()} for model: {model_name}")
        
        test_mode = parsed_args.get("test_mode")
        if test_mode:
            print(f"Test mode: {test_mode}")
        else:
            print(f"Full evaluation")
    
    def _process_results(self, model_log_dir: str, recent_dir: str, parsed_args: Dict[str, Any]) -> None:
        """Process and copy results after evaluation."""
        # Find the eval log file in the model_log_dir
        eval_files = glob.glob(os.path.join(model_log_dir, "*.eval"))
        
        if eval_files:
            eval_file = eval_files[0]  # Should only be one
            eval_filename = os.path.basename(eval_file)
            
            # Generate results using config-specific processor
            print(f"📊 Generating results...")
            try:
                results_processor = self.config.get_results_processor(parsed_args)
                success = results_processor(eval_file, force_overwrite=True)
                
                if success:
                    print(f"✅ Results generated in: {model_log_dir}")
                    
                    # Copy all generated files to recent_result
                    self._copy_results_to_recent(eval_file, model_log_dir, recent_dir, eval_filename)
                    
                    print(f"\\n✅ All files available in: {recent_dir}/")
                else:
                    print("⚠️  Results generation failed")
            except Exception as e:
                print(f"⚠️  Error generating results: {e}")
        else:
            print("⚠️  Warning: No .eval file found in log directory")
    
    def _copy_results_to_recent(self, eval_file: str, model_log_dir: str, recent_dir: str, eval_filename: str) -> None:
        """Copy results files to recent_result directory."""
        # Copy the eval file
        recent_eval_path = os.path.join(recent_dir, eval_filename)
        shutil.copy2(eval_file, recent_eval_path)
        print(f"📄 Eval file copied to recent_result: {eval_filename}")
        
        # Copy all result files (different eval types may generate different files)
        result_files = ['group_results.json', 'options_results.json', 'experiment_results.json', 'experiment_report.md']
        copied_files = []
        for result_file in result_files:
            result_path = os.path.join(model_log_dir, result_file)
            if os.path.exists(result_path):
                shutil.copy2(result_path, os.path.join(recent_dir, result_file))
                copied_files.append(result_file)
        
        if copied_files:
            print(f"📄 Results copied to recent_result: {', '.join(copied_files)}")


def run_evaluation(model_name: str, config: EvalConfig, args: List[str]) -> str:
    """
    Convenience function to run an evaluation with the given configuration.
    
    Args:
        model_name: Name of the model to evaluate
        config: Evaluation configuration
        args: Command line arguments
        
    Returns:
        Path to the generated .eval file
    """
    runner = EvalRunner(config)
    runner.run(model_name, args)
    
    # Return the path to the generated eval file
    import glob
    eval_files = glob.glob("recent_result/*.eval")
    if eval_files:
        return eval_files[0]
    else:
        raise RuntimeError("No .eval file found in recent_result directory")