#!/usr/bin/env python3
"""
Test script to run quick tests for all three evaluation types simultaneously.
This helps verify that changes haven't broken any of the evaluation systems.
"""

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# ANSI color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def run_eval(eval_name, script_path):
    """Run a single evaluation and return the results."""
    print(f"{BLUE}Starting {eval_name}...{RESET}")
    
    try:
        # Run the evaluation script
        result = subprocess.run(
            [
                sys.executable,
                script_path,
                "groq/llama-3.3-70b-versatile",
                "quick-test"
            ],
            capture_output=True,
            text=True,
            env={**subprocess.os.environ, "PYTHONPATH": "."}
        )
        
        # Check if successful
        if result.returncode == 0 and "✅ All files available in: recent_result/" in result.stdout:
            return {
                "name": eval_name,
                "status": "success",
                "output": result.stdout,
                "error": None
            }
        else:
            return {
                "name": eval_name,
                "status": "failed",
                "output": result.stdout,
                "error": result.stderr or "No success message found"
            }
    except Exception as e:
        return {
            "name": eval_name,
            "status": "error",
            "output": None,
            "error": str(e)
        }

def main():
    """Run all evaluations in parallel and report results."""
    print(f"{BOLD}🧪 Running quick tests for all evaluation types...{RESET}")
    print(f"Model: {YELLOW}groq/llama-3.3-70b-versatile{RESET}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Define the evaluations to run
    evaluations = [
        ("Base Evaluation", "scripts/run_base_eval.py"),
        ("Effort Reasoning Evaluation", "scripts/run_effort_reasoning_eval.py"),
        ("Token Reasoning Evaluation", "scripts/run_token_reasoning_eval.py")
    ]
    
    # Check that we're in the right directory
    if not Path("scripts/run_base_eval.py").exists():
        print(f"{RED}Error: Must run from the silent_agreement_v1 directory!{RESET}")
        print("Please cd to the correct directory and activate the virtual environment.")
        sys.exit(1)
    
    # Run evaluations in parallel
    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all tasks
        future_to_eval = {
            executor.submit(run_eval, name, script): name 
            for name, script in evaluations
        }
        
        # Process results as they complete
        for future in as_completed(future_to_eval):
            result = future.result()
            results.append(result)
    
    # Sort results by original order
    results.sort(key=lambda x: [name for name, _ in evaluations].index(x["name"]))
    
    # Display summary
    print(f"\n{BOLD}📊 Test Results Summary:{RESET}")
    print("=" * 50)
    
    all_passed = True
    for result in results:
        if result["status"] == "success":
            status_icon = "✅"
            status_color = GREEN
        else:
            status_icon = "❌"
            status_color = RED
            all_passed = False
        
        print(f"{status_icon} {result['name']}: {status_color}{result['status'].upper()}{RESET}")
        
        if result["status"] != "success" and result["error"]:
            print(f"   Error: {result['error'][:100]}...")
    
    print("=" * 50)
    
    # Final verdict
    if all_passed:
        print(f"\n{GREEN}{BOLD}✅ All evaluations passed!{RESET}")
        print("The evaluation framework is working correctly.")
        return 0
    else:
        print(f"\n{RED}{BOLD}❌ Some evaluations failed!{RESET}")
        print("Please check the errors above.")
        
        # Show detailed output for failed tests
        failed_tests = [r for r in results if r["status"] != "success"]
        if failed_tests and input("\nShow detailed output for failed tests? (y/n): ").lower() == 'y':
            for result in failed_tests:
                print(f"\n{YELLOW}Detailed output for {result['name']}:{RESET}")
                print("-" * 50)
                if result["output"]:
                    print(result["output"][-1000:])  # Last 1000 chars
                if result["error"]:
                    print(f"\nError output:\n{result['error']}")
                print("-" * 50)
        
        return 1

if __name__ == "__main__":
    # Ensure the script is executable
    script_path = Path(__file__)
    if not script_path.stat().st_mode & 0o111:
        script_path.chmod(script_path.stat().st_mode | 0o111)
    
    sys.exit(main())