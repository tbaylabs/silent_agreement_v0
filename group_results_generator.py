from typing import Dict
import json

def group_results_generator(grouped_data: Dict[str, Dict]) -> None:
    """Generate group_results.json from grouped scores data."""
    output_data = {}
    for key, group in grouped_data.items():
        # Create response distribution with all values set to 0
        options = group["options_list"]
        response_dist = {option: 0 for option in options}
        response_dist["invalid"] = 0  # Add invalid category
        
        output_data[key] = {
            "option_id": group["option_id"],
            "options_list": group["options_list"],
            "option_name": group["option_name"],
            "option_type": group["option_type"],
            "condition": group["condition"],
            "score_count": len(group["scores"]),
            "response_distribution": response_dist
        }
    
    # Write to file, overwriting if it exists
    with open("group_results.json", "w") as f:
        json.dump(output_data, f, indent=2)
