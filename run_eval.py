#!/usr/bin/env python3
"""
Custom entrypoint for running Silent Agreement evaluations.
Handles log file placement in model-specific dated folders and recent_results.
Uses --log-dir parameter to specify custom log location.
"""

import os
import sys
import shutil
import glob
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from inspect_ai import eval
from sa_v0_remastered import sa_test


def main():
    # Load environment variables from .env file (search up the directory tree)
    env_file = find_dotenv()
    if env_file:
        print(f"Loading environment from: {env_file}")
        load_dotenv(env_file)
    else:
        print("No .env file found - API keys may not be available")
    
    if len(sys.argv) != 2:
        print("Usage: python run_eval.py <model_name>")
        print("Example: python run_eval.py gpt-4o")
        sys.exit(1)
    
    model_name = sys.argv[1]
    
    # Create timestamp for this run
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Convert model name to folder structure
    # openai/gpt-4o -> openai/gpt-4o
    # openai/azure/gpt-4o -> openai_azure/gpt-4o  
    if model_name.count('/') > 1:
        # Multiple slashes: replace all but the last slash with underscore
        parts = model_name.split('/')
        folder_path = '_'.join(parts[:-1]) + '/' + parts[-1]
    else:
        # Single slash: keep as is
        folder_path = model_name
    
    # Set up log directory for this specific run
    model_log_dir = os.path.join('results', folder_path, timestamp)
    os.makedirs(model_log_dir, exist_ok=True)
    
    # Clear and recreate recent_result directory
    recent_dir = 'recent_result'
    if os.path.exists(recent_dir):
        shutil.rmtree(recent_dir)
    os.makedirs(recent_dir, exist_ok=True)
    
    print(f"Running eval for model: {model_name}")
    print(f"Logs will be saved to: {model_log_dir}")
    
    try:
        # Run the evaluation with custom log directory and JSON generation enabled
        logs = eval(sa_test(generate_json_results=True), model=model_name, log_dir=model_log_dir)
        log = logs[0]  # Get the first (and only) log
        
        if log.status == "success":
            print(f"✅ Evaluation completed successfully!")
            
            # Find the eval log file in the model_log_dir
            eval_files = glob.glob(os.path.join(model_log_dir, "*.eval"))
            
            if eval_files:
                eval_file = eval_files[0]  # Should only be one
                eval_filename = os.path.basename(eval_file)
                
                # Copy to recent_result directory
                recent_dir = 'recent_result'
                
                recent_eval_path = os.path.join(recent_dir, eval_filename)
                shutil.copy2(eval_file, recent_eval_path)
                
                print(f"📄 Log file copied to recent_result: {eval_filename}")
            else:
                print("⚠️  Warning: No .eval file found in log directory")
                
        else:
            print(f"❌ Evaluation failed with status: {log.status}")
            if hasattr(log, 'error') and log.error:
                print(f"Error: {log.error}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error running evaluation: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()