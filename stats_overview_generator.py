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
        "absolute_metrics": {
            metric: {cond: 0.0 for cond in conditions}
            for metric in metrics
        },
        "difference_metrics": {
            metric: {pair: 0.0 for pair in diff_pairs}
            for metric in metrics
        },
        "counts": {
            "total": {cond: 0 for cond in conditions},
            "valid": {cond: 0 for cond in conditions}
        }
    }
    
    option_count = 0
    
    # Sum up values across all options
    for option_data in options_results.values():
        overview = option_data["overview"]
        differences = option_data.get("differences", {})
        
        # Only include options that have all conditions
        if all(cond in overview["top_prop_include_invalid"] for cond in conditions):
            option_count += 1
            
            # Sum metric values
            for metric in metrics:
                for condition in conditions:
                    totals["absolute_metrics"][metric][condition] += overview[metric][condition]
            
            # Sum difference values
            for metric in metrics:
                for pair in diff_pairs:
                    totals["difference_metrics"][metric][pair] += differences[metric][pair]
            
            # Sum counts
            for condition in conditions:
                condition_data = option_data["conditions"][condition]["trial_block_stats"]
                totals["counts"]["total"][condition] += condition_data["total_response_count"]
                totals["counts"]["valid"][condition] += condition_data["valid_response_count"]
    
    # Calculate means and totals
    stats_overview = {
        "absolute_metrics": {
            metric: {
                f"{cond}_mean": round(totals["absolute_metrics"][metric][condition] / option_count, 3)
                for cond in conditions
            }
            for metric in metrics
        },
        "difference_metrics": {
            metric: {
                pair: round(totals["difference_metrics"][metric][pair] / option_count, 3)
                for pair in diff_pairs
            }
            for metric in metrics
        },
        "meta": {
            "total_invalid_count": sum(totals["counts"]["total"][cond] - totals["counts"]["valid"][cond] for cond in conditions),
            "total_valid_count": sum(totals["counts"]["valid"][cond] for cond in conditions)
        }
    }
    
    # Add count means to absolute_metrics
    stats_overview["absolute_metrics"]["total_count"] = {
        f"{cond}_mean": round(totals["counts"]["total"][cond] / option_count, 3)
        for cond in conditions
    }
    stats_overview["absolute_metrics"]["valid_count"] = {
        f"{cond}_mean": round(totals["counts"]["valid"][cond] / option_count, 3)
        for cond in conditions
    }
    
    # Write to file
    with open("stats_overview.json", "w") as f:
        json.dump(stats_overview, f, indent=2)
