#!/usr/bin/env python3
"""
Bulk regenerate JSON results for all eval files in results/ and test_results/ directories.
Useful for regenerating all results after changes to the analysis code.
"""

import os
import sys
import glob
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from results_generators.generate_json_results import generate_json_results_from_eval


def find_eval_files(base_dirs):
    """Find all .eval files in the given directories and their subdirectories."""
    eval_files = []
    
    for base_dir in base_dirs:
        if os.path.exists(base_dir):
            pattern = os.path.join(base_dir, "**/*.eval")
            files = glob.glob(pattern, recursive=True)
            eval_files.extend(files)
            print(f"Found {len(files)} eval files in {base_dir}/")
    
    return sorted(eval_files)


def regenerate_single_eval(eval_file):
    """Regenerate JSON results for a single eval file."""
    try:
        print(f"Processing: {eval_file}")
        success = generate_json_results_from_eval(eval_file, force_overwrite=True)
        if success:
            return (eval_file, True, None)
        else:
            return (eval_file, False, "Generation returned False")
    except Exception as e:
        return (eval_file, False, str(e))


def main():
    parser = argparse.ArgumentParser(description="Bulk regenerate JSON results for eval files")
    parser.add_argument("--results", action="store_true", help="Process results/ directory")
    parser.add_argument("--test-results", action="store_true", help="Process test_results/ directory")
    parser.add_argument("--pattern", help="Only process files matching this pattern (e.g., '*gpt-4o*')")
    parser.add_argument("--dry-run", action="store_true", help="Show which files would be processed without actually processing them")
    parser.add_argument("--parallel", type=int, default=4, help="Number of parallel workers (default: 4)")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")
    
    args = parser.parse_args()
    
    # Determine which directories to process
    base_dirs = []
    if args.results:
        base_dirs.append("data/results")
    if args.test_results:
        base_dirs.append("data/test_results")
    
    # If neither specified, process both
    if not base_dirs:
        base_dirs = ["data/results", "data/test_results"]
    
    # Find all eval files
    eval_files = find_eval_files(base_dirs)
    
    if not eval_files:
        print("No eval files found.")
        return
    
    # Apply pattern filter if specified
    if args.pattern:
        import fnmatch
        filtered = [f for f in eval_files if fnmatch.fnmatch(f, args.pattern)]
        print(f"Filtered to {len(filtered)} files matching pattern '{args.pattern}'")
        eval_files = filtered
    
    print(f"\nTotal eval files to process: {len(eval_files)}")
    
    if args.dry_run:
        print("\nDRY RUN - Files that would be processed:")
        for eval_file in eval_files:
            print(f"  {eval_file}")
        return
    
    # Confirm before proceeding
    if not args.yes:
        response = input("\nProceed with regeneration? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Cancelled.")
            return
    
    print(f"\nProcessing {len(eval_files)} files with {args.parallel} workers...")
    
    # Process files in parallel
    successful = 0
    failed = []
    
    with ProcessPoolExecutor(max_workers=args.parallel) as executor:
        # Submit all tasks
        future_to_file = {executor.submit(regenerate_single_eval, eval_file): eval_file 
                          for eval_file in eval_files}
        
        # Process completed tasks
        for future in as_completed(future_to_file):
            eval_file, success, error = future.result()
            if success:
                successful += 1
                print(f"✅ {eval_file}")
            else:
                failed.append((eval_file, error))
                print(f"❌ {eval_file}: {error}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Summary: {successful} successful, {len(failed)} failed")
    
    if failed:
        print("\nFailed files:")
        for eval_file, error in failed:
            print(f"  {eval_file}: {error}")
    
    print("\n✅ Bulk regeneration complete!")


if __name__ == "__main__":
    main()