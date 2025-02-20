from typing import Dict, Any
import json

def generate_stats_overview(options_results: Dict[str, Any]) -> None:
    """
    Generate overview statistics across all options.
    Writes results to stats_overview.json only if all data meets validity criteria.
    """
    # Validate data before proceeding
    for option_data in options_results.values():
        # Check if differences exists and is not empty
        if not option_data.get("differences"):
            print("Skipping stats overview generation: some options missing differences data")
            return
            
        # Check if all conditions have valid response counts
        for condition_data in option_data["conditions"].values():
            if condition_data["trial_block_stats"]["total_response_count"] < 1:
                print("Skipping stats overview generation: some conditions have no responses")
                return

    # Initialize accumulators for each metric and condition
    metrics = ["top_prop_include_invalid", "top_prop_exclude_invalid"]
    conditions = ["control_suppress_cot", "coordinate_suppress_cot", "coordinate_elicit_cot"]
    diff_pairs = [
        "coordinate_suppress_cot_vs_control",
        "coordinate_elicit_cot_vs_control",
        "coordinate_elicit_cot_vs_suppress_cot"
    ]
    
    totals = {
        "conditions": {
            metric: {cond: 0.0 for cond in conditions}
            for metric in metrics
        },
        "differences": {
            metric: {pair: 0.0 for pair in diff_pairs}
            for metric in metrics
        }
    }
    
    # Count valid options (those with all conditions present)
    valid_option_count = 0
    
    # Sum up values across all options
    for option_data in options_results.values():
        overview = option_data["overview"]
        differences = option_data.get("differences", {})
        
        # Only include options that have all conditions
        if all(cond in overview["top_prop_include_invalid"] for cond in conditions):
            valid_option_count += 1
            
            # Sum condition values
            for metric in metrics:
                for condition in conditions:
                    totals["conditions"][metric][condition] += overview[metric][condition]
            
            # Sum difference values
            for metric in metrics:
                for pair in diff_pairs:
                    totals["differences"][metric][pair] += differences[metric][pair]
    
    # Calculate means
    stats_overview = {
        "conditions": {
            metric: {
                cond: round(totals["conditions"][metric][cond] / valid_option_count, 3)
                for cond in conditions
            }
            for metric in metrics
        },
        "differences": {
            metric: {
                pair: round(totals["differences"][metric][pair] / valid_option_count, 3)
                for pair in diff_pairs
            }
            for metric in metrics
        },
        "meta": {
            "valid_option_count": valid_option_count
        }
    }
    
    # Write to file
    with open("stats_overview.json", "w") as f:
        json.dump(stats_overview, f, indent=2)
