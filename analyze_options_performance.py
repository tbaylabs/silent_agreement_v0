#!/usr/bin/env python3
"""
Script to analyze options_results.json files across all models and create a comparison table.
Shows top_prop_exclude_invalid scores for each option across different models.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
from tabulate import tabulate
from datetime import datetime

def find_options_results_files(base_path: Path) -> List[Tuple[str, Path]]:
    """Find all options_results.json files and extract model names."""
    results = []
    
    # Navigate through the folder structure: base/{provider}/{model}/{timestamp}/options_results.json
    for provider_dir in base_path.iterdir():
        if provider_dir.is_dir():
            for model_dir in provider_dir.iterdir():
                if model_dir.is_dir():
                    # Find the most recent timestamp directory
                    timestamp_dirs = sorted([d for d in model_dir.iterdir() if d.is_dir()], 
                                          key=lambda x: x.name, reverse=True)
                    
                    for timestamp_dir in timestamp_dirs:
                        options_file = timestamp_dir / "options_results.json"
                        if options_file.exists():
                            # Create a model identifier
                            model_name = f"{provider_dir.name}/{model_dir.name}"
                            results.append((model_name, options_file))
                            break  # Only take the most recent result for each model
    
    return sorted(results)

def extract_control_scores(options_results: Dict) -> Tuple[Dict[str, float], Dict[str, List[str]]]:
    """Extract top_prop_exclude_invalid scores from control condition for each option."""
    scores = {}
    options_lists = {}
    
    for option_id, data in options_results.items():
        if isinstance(data, dict) and "trial_blocks_by_condition" in data:
            control_data = data["trial_blocks_by_condition"].get("control", {})
            stats = control_data.get("stats", {})
            score = stats.get("top_prop_exclude_invalid", None)
            if score is not None:
                scores[option_id] = score
            
            # Extract the options list
            if "options_list" in data:
                options_lists[option_id] = data["options_list"]
    
    return scores, options_lists

def main():
    # Path to the base results directory
    base_path = Path("/Users/graemeford/TBayLabs/silent_agreement/silent_agreement_v1/data/results/base")
    
    if not base_path.exists():
        print(f"Error: Results directory not found at {base_path}")
        return
    
    # Find all options_results.json files
    model_files = find_options_results_files(base_path)
    
    if not model_files:
        print("No options_results.json files found")
        return
    
    print(f"Found {len(model_files)} models with results:\n")
    
    # Collect all data
    all_data = {}
    all_options = set()
    all_options_lists = {}
    
    for model_name, file_path in model_files:
        print(f"Processing: {model_name}")
        
        try:
            with open(file_path, 'r') as f:
                options_results = json.load(f)
            
            scores, options_lists = extract_control_scores(options_results)
            all_data[model_name] = scores
            all_options.update(scores.keys())
            # Merge options lists (they should be the same across models)
            all_options_lists.update(options_lists)
            
        except Exception as e:
            print(f"  Error reading {file_path}: {e}")
    
    # Sort options for consistent ordering
    sorted_options = sorted(all_options)
    
    # Create table data
    table_data = []
    headers = ["Option", "Options List"] + sorted(all_data.keys())
    
    for option in sorted_options:
        row = [option]
        # Add the options list
        options_list = all_options_lists.get(option, [])
        if options_list:
            # Check if it's a symbol or text option
            if "|symbol" in option:
                # Show all symbols
                options_str = ", ".join(options_list)
            else:
                # For text, show first option followed by ...
                options_str = f"{options_list[0]}, ..."
        else:
            options_str = "-"
        row.append(options_str)
        # Add scores
        for model_name in sorted(all_data.keys()):
            score = all_data[model_name].get(option, None)
            row.append(f"{score:.3f}" if score is not None else "-")
        table_data.append(row)
    
    # Print the table
    print("\n\nOption Performance Across Models (top_prop_exclude_invalid in control condition)")
    print("=" * 120)
    print(tabulate(table_data, headers=headers, tablefmt='pipe', floatfmt='.3f'))
    
    # Save to CSV for further analysis
    output_csv = base_path.parent / "options_performance_comparison.csv"
    with open(output_csv, 'w') as f:
        # Write headers
        f.write(",".join(headers) + "\n")
        # Write data
        for row in table_data:
            f.write(",".join(str(x) for x in row) + "\n")
    print(f"\nResults saved to: {output_csv}")
    
    # Save as markdown file with nicely formatted table
    output_md = base_path.parent / "options_performance_comparison.md"
    with open(output_md, 'w') as f:
        f.write("# Options Performance Comparison\n\n")
        f.write("## Top Proportion Excluding Invalid (Control Condition)\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(tabulate(table_data, headers=headers, tablefmt='pipe', floatfmt='.3f'))
        f.write("\n\n## Summary Statistics\n\n")
        
        # Write summary stats
        for model_name in sorted(all_data.keys()):
            scores = [v for v in all_data[model_name].values() if v is not None]
            if scores:
                avg_score = sum(scores) / len(scores)
                min_score = min(scores)
                max_score = max(scores)
                f.write(f"**{model_name}**\n")
                f.write(f"- Average: {avg_score:.3f}\n")
                f.write(f"- Min: {min_score:.3f}\n")
                f.write(f"- Max: {max_score:.3f}\n")
                f.write(f"- N: {len(scores)}\n\n")
    
    print(f"Markdown table saved to: {output_md}")
    
    # Calculate some summary statistics
    print("\n\nSummary Statistics:")
    print("-" * 40)
    
    for model_name in sorted(all_data.keys()):
        scores = [v for v in all_data[model_name].values() if v is not None]
        if scores:
            avg_score = sum(scores) / len(scores)
            print(f"{model_name}: avg={avg_score:.3f}, n={len(scores)}")

if __name__ == "__main__":
    main()