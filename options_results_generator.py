from typing import Dict, Any
import json

def generate_options_results(group_results: Dict[str, Any]) -> None:
    """
    Reorganize group results by option_id and condition.
    Writes results to results_by_option.json
    """
    options_grouped: Dict[str, Dict] = {}
    
    # First pass: gather data as before
    for key, group in group_results.items():
        option_id = group["option_id"]
        condition = group["condition"]
        
        if option_id not in options_grouped:
            options_grouped[option_id] = {
                "options_list": group["options_list"],
                "overview": {
                    "top_prop_include_invalid": {},
                    "top_prop_exclude_invalid": {}
                },
                "differences": {},
                "conditions": {},
                "options_id": option_id,
                "options_type": group["option_type"]
            }
        
        response_dist = group["response_distribution"]
        total_responses = group["score_count"]
        invalid_count = response_dist["invalid"]
        valid_responses = total_responses - invalid_count
        
        top_include = round(max(response_dist.values()) / total_responses if total_responses > 0 else 0, 3)
        top_exclude = round(max(response_dist.values()) / valid_responses if valid_responses > 0 else 0, 3)
        
        # Add to overview
        options_grouped[option_id]["overview"]["top_prop_include_invalid"][condition] = top_include
        options_grouped[option_id]["overview"]["top_prop_exclude_invalid"][condition] = top_exclude
        
        # Add to conditions
        options_grouped[option_id]["conditions"][condition] = {
            "response_distribution": response_dist,
            "trial_block_stats": {
                "total_response_count": total_responses,
                "valid_response_count": valid_responses,
                "top_prop_include_invalid": top_include,
                "top_prop_exclude_invalid": top_exclude
            }
        }
    
    # Second pass: calculate differences
    for option_data in options_grouped.values():
        conditions = option_data["conditions"]
        
        # Calculate differences if all required conditions exist
        if all(cond in conditions for cond in ["control_suppress_cot", "coordinate_suppress_cot", "coordinate_elicit_cot"]):
            option_data["differences"] = {
                "coordinate_suppress_cot_vs_control": {
                    "top_prop_include_invalid_diff": round(
                        conditions["coordinate_suppress_cot"]["trial_block_stats"]["top_prop_include_invalid"] -
                        conditions["control_suppress_cot"]["trial_block_stats"]["top_prop_include_invalid"], 
                        3
                    ),
                    "top_prop_exclude_invalid_diff": round(
                        conditions["coordinate_suppress_cot"]["trial_block_stats"]["top_prop_exclude_invalid"] -
                        conditions["control_suppress_cot"]["trial_block_stats"]["top_prop_exclude_invalid"],
                        3
                    )
                },
                "coordinate_elicit_cot_vs_control": {
                    "top_prop_include_invalid_diff": round(
                        conditions["coordinate_elicit_cot"]["trial_block_stats"]["top_prop_include_invalid"] -
                        conditions["control_suppress_cot"]["trial_block_stats"]["top_prop_include_invalid"],
                        3
                    ),
                    "top_prop_exclude_invalid_diff": round(
                        conditions["coordinate_elicit_cot"]["trial_block_stats"]["top_prop_exclude_invalid"] -
                        conditions["control_suppress_cot"]["trial_block_stats"]["top_prop_exclude_invalid"],
                        3
                    )
                },
                "coordinate_elicit_cot_vs_suppress_cot": {
                    "top_prop_include_invalid_diff": round(
                        conditions["coordinate_elicit_cot"]["trial_block_stats"]["top_prop_include_invalid"] -
                        conditions["coordinate_suppress_cot"]["trial_block_stats"]["top_prop_include_invalid"],
                        3
                    ),
                    "top_prop_exclude_invalid_diff": round(
                        conditions["coordinate_elicit_cot"]["trial_block_stats"]["top_prop_exclude_invalid"] -
                        conditions["coordinate_suppress_cot"]["trial_block_stats"]["top_prop_exclude_invalid"],
                        3
                    )
                }
            }

    # Write to file
    with open("results_by_option.json", "w") as f:
        json.dump(options_grouped, f, indent=2)
