from typing import Dict, Any
import json

def generate_options_results(group_results: Dict[str, Any]) -> None:
    """
    Reorganize group results by option_id and condition.
    Writes results to results_by_option.json
    """
    # First, group the data by option_id
    options_grouped: Dict[str, Dict] = {}
    
    for key, group in group_results.items():
        option_id = group["option_id"]
        condition = group["condition"]
        
        # Initialize the option group if we haven't seen it before
        if option_id not in options_grouped:
            options_grouped[option_id] = {
                "options_id": option_id,
                "options_type": group["option_type"],
                "options_list": group["options_list"],
                "conditions": {}
            }
        
        # Calculate coordination metrics
        response_dist = group["response_distribution"]
        total_responses = group["score_count"]
        invalid_count = response_dist["invalid"]
        valid_responses = total_responses - invalid_count
        
        # Add the condition data
        options_grouped[option_id]["conditions"][condition] = {
            "response_distribution": response_dist,
            "trial_block_stats": {
                "total_response_count": total_responses,
                "valid_response_count": valid_responses,
                "top_prop_include_invalid": round(max(response_dist.values()) / total_responses if total_responses > 0 else 0, 3),
                "top_prop_exclude_invalid": round(max(response_dist.values()) / valid_responses if valid_responses > 0 else 0, 3)
            }
        }
    
    # Write to file
    with open("results_by_option.json", "w") as f:
        json.dump(options_grouped, f, indent=2)
