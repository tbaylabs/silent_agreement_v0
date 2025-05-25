#!/usr/bin/env python3
"""
Bulk generate JSON results for all eval logs in the results directory.
Finds all dated folders and runs the JSON results generator on their .eval files.
"""

import os
import glob
import subprocess
import sys
from pathlib import Path

def find_all_eval_logs(results_dir: str = "results") -> list[str]:
    """Find all .eval files in dated folders within the results directory."""
    pattern = os.path.join(results_dir, "**", "*.eval")
    all_eval_logs = glob.glob(pattern, recursive=True)
    
    # Filter to only include files in dated folders (folders that look like 20YYMMDD_HHMMSS)
    dated_eval_logs = []
    for eval_log in all_eval_logs:
        path_parts = Path(eval_log).parts
        # Look for a dated folder pattern in the path
        for part in path_parts:
            if len(part) == 15 and part[8] == '_' and part[:8].isdigit() and part[9:].isdigit():
                dated_eval_logs.append(eval_log)
                break
    
    return dated_eval_logs

def main():
    print("🔍 Finding all eval logs in dated folders...")
    eval_logs = find_all_eval_logs()
    
    if not eval_logs:
        print("❌ No eval logs found in dated folders")
        sys.exit(1)
    
    print(f"📋 Found {len(eval_logs)} eval logs to process:")
    for log in eval_logs:
        print(f"  - {log}")
    
    print(f"\n🚀 Starting bulk regeneration...")
    
    success_count = 0
    failed_logs = []
    
    for i, eval_log in enumerate(eval_logs, 1):
        print(f"\n{'='*80}")
        print(f"[{i}/{len(eval_logs)}] Processing: {eval_log}")
        print('='*80)
        
        try:
            # Run the JSON results generator on this eval log (with --force to skip prompts)
            result = subprocess.run([
                sys.executable, "results_generators/generate_json_results.py", eval_log, "--force"
            ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            if result.returncode == 0:
                print(f"✅ Successfully processed {eval_log}")
                success_count += 1
            else:
                print(f"❌ Failed to process {eval_log}")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                failed_logs.append(eval_log)
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout processing {eval_log}")
            failed_logs.append(eval_log)
        except Exception as e:
            print(f"💥 Error processing {eval_log}: {str(e)}")
            failed_logs.append(eval_log)
    
    print(f"\n{'='*80}")
    print("📊 BULK REGENERATION SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Successfully processed: {success_count}/{len(eval_logs)} eval logs")
    
    if failed_logs:
        print(f"❌ Failed to process {len(failed_logs)} eval logs:")
        for failed_log in failed_logs:
            print(f"  - {failed_log}")
        sys.exit(1)
    else:
        print("🎉 All eval logs processed successfully!")

if __name__ == "__main__":
    main()