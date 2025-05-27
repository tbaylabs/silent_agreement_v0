#!/usr/bin/env python3
"""
Bulk regenerate JSON results and reports for all eval files in the results directory.
This script finds all .eval files and regenerates options_results.json, experiment_results.json,
and experiment_report.md for each one.
"""

import os
import sys
import glob
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
from results_generators.generate_json_results import generate_json_results_from_eval


def find_eval_files(base_dir: str) -> list[str]:
    """Find all .eval files in the given directory and its subdirectories."""
    eval_files = []
    
    # Use glob to find all .eval files recursively
    pattern = os.path.join(base_dir, "**/*.eval")
    eval_files = glob.glob(pattern, recursive=True)
    
    return sorted(eval_files)


def process_eval_file(eval_path: str) -> tuple[str, bool, str]:
    """
    Process a single eval file and regenerate its JSON results.
    Returns (eval_path, success, message)
    """
    try:
        print(f"Processing: {eval_path}")
        success = generate_json_results_from_eval(eval_path, force_overwrite=True)
        
        if success:
            return (eval_path, True, "Success")
        else:
            return (eval_path, False, "Failed to generate results")
            
    except Exception as e:
        return (eval_path, False, f"Error: {str(e)}")


def main():
    """Main function to orchestrate bulk regeneration."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Bulk regenerate JSON results for all eval files"
    )
    parser.add_argument(
        "--parallel", 
        action="store_true",
        help="Process files in parallel (faster but may use more memory)"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="Maximum number of parallel workers (defaults to CPU count)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without actually regenerating"
    )
    
    args = parser.parse_args()
    
    # Find all eval files in results directory
    results_dir = "results"
    recent_dir = "recent_result"
    
    print("🔍 Searching for eval files...")
    
    eval_files = []
    
    # Find files in results directory
    if os.path.exists(results_dir):
        results_files = find_eval_files(results_dir)
        eval_files.extend(results_files)
        print(f"Found {len(results_files)} eval files in {results_dir}/")
    
    # Find files in recent_result directory
    if os.path.exists(recent_dir):
        recent_files = find_eval_files(recent_dir)
        eval_files.extend(recent_files)
        print(f"Found {len(recent_files)} eval files in {recent_dir}/")
    
    if not eval_files:
        print("❌ No eval files found!")
        return
    
    print(f"\n📊 Total eval files to process: {len(eval_files)}")
    
    # If dry run, just show the files and exit
    if args.dry_run:
        print("\n🔍 DRY RUN - Files that would be processed:\n")
        for eval_file in eval_files:
            print(f"  - {eval_file}")
        print("\nNo files were modified (dry run mode)")
        return
    
    # Confirm with user
    response = input("\nThis will overwrite all existing JSON results and reports. Continue? (y/N): ")
    if response.lower() != 'y':
        print("❌ Operation cancelled.")
        return
    
    print("\n🚀 Starting bulk regeneration...\n")
    
    # Process files
    success_count = 0
    failure_count = 0
    results = []
    
    if args.parallel:
        # Process in parallel
        max_workers = args.max_workers or multiprocessing.cpu_count()
        print(f"Processing in parallel with {max_workers} workers...\n")
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_eval = {
                executor.submit(process_eval_file, eval_path): eval_path 
                for eval_path in eval_files
            }
            
            # Process completed tasks
            for future in as_completed(future_to_eval):
                eval_path, success, message = future.result()
                results.append((eval_path, success, message))
                
                if success:
                    success_count += 1
                    print(f"✅ {eval_path}")
                else:
                    failure_count += 1
                    print(f"❌ {eval_path}: {message}")
    else:
        # Process sequentially
        print("Processing sequentially...\n")
        
        for i, eval_path in enumerate(eval_files, 1):
            print(f"[{i}/{len(eval_files)}] ", end="")
            eval_path, success, message = process_eval_file(eval_path)
            results.append((eval_path, success, message))
            
            if success:
                success_count += 1
                print(f"✅ {eval_path}")
            else:
                failure_count += 1
                print(f"❌ {eval_path}: {message}")
    
    # Summary
    print("\n" + "="*60)
    print("📈 BULK REGENERATION COMPLETE")
    print("="*60)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failure_count}")
    print(f"📊 Total: {len(eval_files)}")
    
    # Show failures if any
    if failure_count > 0:
        print("\n❌ Failed files:")
        for eval_path, success, message in results:
            if not success:
                print(f"  - {eval_path}: {message}")
    
    print("\n✨ All done!")


if __name__ == "__main__":
    # Ensure we're running from the project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    # Add parent directory to path so imports work
    sys.path.insert(0, str(project_root))
    
    main()