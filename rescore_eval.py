#!/usr/bin/env python3
"""
Regenerate metrics script for Silent Agreement evaluations.
Takes existing eval log files and regenerates JSON files with updated metrics,
using the existing scores without re-running the scorer.
"""

import os
import sys
import glob
import json
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from inspect_ai.log import read_eval_log
from inspect_ai.scorer import SampleScore
from group_results_generator import group_results_generator
from options_results_generator import generate_options_results  
from stats_overview_generator import generate_stats_overview

# Load environment variables
load_dotenv(find_dotenv())


def regenerate_metrics(eval_log_path: str, output_dir: str = None):
    """
    Regenerate metrics from an existing eval log using existing scores.
    
    Args:
        eval_log_path: Path to the .eval log file
        output_dir: Directory to save new JSON files (defaults to same dir as eval log)
    """
    
    print(f"Regenerating metrics from eval log: {eval_log_path}")
    
    # Read the eval log
    log = read_eval_log(eval_log_path)
    
    if log.status != "success":
        print(f"Warning: Eval log status is '{log.status}', not 'success'")
        return False
    
    # Determine output directory
    if output_dir is None:
        output_dir = os.path.dirname(eval_log_path)
    
    # Remember original directory and script directory
    original_cwd = os.getcwd()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        print(f"Processing {len(log.samples)} samples...")
        
        # Extract existing scores from samples and add token counting
        sample_scores = []
        for sample in log.samples:
            # Calculate token count from completion
            completion = sample.output.completion if hasattr(sample.output, 'completion') else str(sample.output)
            token_count = len(completion.split()) if completion else 0
            
            # Get existing score and add token count to metadata
            existing_score = sample.score
            if existing_score.metadata:
                updated_metadata = existing_score.metadata.copy()
            else:
                updated_metadata = {}
            updated_metadata["token_count"] = token_count
            
            # Create new score with updated metadata
            from inspect_ai.scorer import Score
            updated_score = Score(
                value=existing_score.value,
                answer=existing_score.answer,
                explanation=existing_score.explanation,
                metadata=updated_metadata
            )
            
            # Create SampleScore object
            sample_score = SampleScore(
                sample_id=sample.id,
                sample_metadata=sample.metadata,
                score=updated_score,
                scorer_metadata=sample.scorer if hasattr(sample, 'scorer') else {}
            )
            sample_scores.append(sample_score)
        
        print(f"Extracted {len(sample_scores)} existing scores")
        
        # Generate the grouped scores data structure that the generators expect
        grouped_scores = {}
        
        # Load options list once
        options_file = os.path.join(script_dir, 'dataset_generation/options_lists/options_lists_v0.json')
        with open(options_file, 'r') as f:
            options_lists = json.load(f)
        
        for sample_score in sample_scores:
            option_id = sample_score.sample_metadata["option_id"]
            condition = sample_score.sample_metadata["condition"] 
            key = f"{condition}-{option_id}"
            
            if key not in grouped_scores:
                # Parse option_id into name and type
                option_name, option_type = option_id.split('|')
                
                grouped_scores[key] = {
                    "option_id": option_id,
                    "options_list": options_lists.get(option_id, []),
                    "option_name": option_name,
                    "option_type": option_type,
                    "condition": condition,
                    "scores": []
                }
            
            grouped_scores[key]["scores"].append(sample_score)
        
        print(f"Grouped into {len(grouped_scores)} condition-option combinations")
        
        # Change to output directory for generating files
        os.chdir(output_dir)
        
        # Generate results using the same pipeline as the original eval
        print("Generating group_results.json...")
        group_results = group_results_generator(grouped_scores)
        
        print("Generating results_by_option.json...")
        options_results = generate_options_results(group_results)
        
        print("Generating stats_overview.json...")
        stats_overview = generate_stats_overview(options_results)
        
        if stats_overview:
            print("✅ Successfully regenerated all JSON files with updated metrics")
        else:
            print("⚠️  Stats overview generation was skipped (likely due to insufficient data)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during metrics regeneration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


def find_eval_logs(results_dir: str = "results") -> list[str]:
    """Find all .eval files in the results directory structure."""
    pattern = os.path.join(results_dir, "**", "*.eval")
    return glob.glob(pattern, recursive=True)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python regenerate_metrics.py <eval_log_path(s)>        # Regenerate single or multiple evals")
        print("  python regenerate_metrics.py --all                     # Regenerate all evals in results/")
        print("  python regenerate_metrics.py --model <model_name>      # Regenerate all evals for a model")
        print("")
        print("Examples:")
        print("  python regenerate_metrics.py results/openai/gpt-4o/20250523_172542/eval.log")
        print("  python regenerate_metrics.py results/llama-3.3-70b-versatile/20250222_125306/*.eval")
        print("  python regenerate_metrics.py --all")
        print("  python regenerate_metrics.py --model openai/gpt-4o")
        sys.exit(1)
    
    if sys.argv[1] == "--all":
        # Regenerate all eval logs
        eval_logs = find_eval_logs()
        print(f"Found {len(eval_logs)} eval logs to regenerate")
        
        success_count = 0
        for eval_log in eval_logs:
            print(f"\n{'='*60}")
            if regenerate_metrics(eval_log):
                success_count += 1
        
        print(f"\n✅ Successfully regenerated {success_count}/{len(eval_logs)} eval logs")
        
    elif sys.argv[1] == "--model":
        if len(sys.argv) < 3:
            print("Error: --model requires a model name")
            sys.exit(1)
        
        model_name = sys.argv[2]
        model_pattern = os.path.join("results", model_name, "**", "*.eval")
        eval_logs = glob.glob(model_pattern, recursive=True)
        
        print(f"Found {len(eval_logs)} eval logs for model '{model_name}' to regenerate")
        
        success_count = 0
        for eval_log in eval_logs:
            print(f"\n{'='*60}")
            if regenerate_metrics(eval_log):
                success_count += 1
        
        print(f"\n✅ Successfully regenerated {success_count}/{len(eval_logs)} eval logs for {model_name}")
        
    else:
        # Regenerate one or more eval logs
        eval_log_paths = sys.argv[1:]
        
        # Filter to only .eval files that exist
        valid_paths = []
        for path in eval_log_paths:
            if not os.path.exists(path):
                print(f"Warning: Eval log file not found: {path}")
                continue
            if not path.endswith('.eval'):
                print(f"Warning: Skipping non-.eval file: {path}")
                continue
            valid_paths.append(path)
        
        if not valid_paths:
            print("Error: No valid .eval files found")
            sys.exit(1)
        
        print(f"Processing {len(valid_paths)} eval log file(s)...")
        
        success_count = 0
        for eval_log_path in valid_paths:
            print(f"\n{'='*60}")
            if regenerate_metrics(eval_log_path):
                success_count += 1
        
        if success_count == len(valid_paths):
            print(f"\n✅ All {success_count} metrics regenerations completed successfully")
        else:
            print(f"\n⚠️ {success_count}/{len(valid_paths)} metrics regenerations completed successfully")
            if success_count == 0:
                sys.exit(1)


if __name__ == "__main__":
    main()