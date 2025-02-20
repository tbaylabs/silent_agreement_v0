from typing import Dict
import json

def group_results_generator(grouped_data: Dict[str, Dict]) -> Dict:
    """Generate group_results.json from grouped scores data."""
    output_data = {}
    for key, group in grouped_data.items():
        # Create response distribution with all values set to 0
        options = group["options_list"]
        response_dist = {option: 0 for option in options}
        response_dist["invalid"] = 0  # Add invalid category
        
        # Count responses
        for sample_score in group["scores"]:
            score = sample_score.score
            if score.value == 0:
                response_dist["invalid"] += 1
            else:
                answer = score.answer
                if answer not in options:
                    raise ValueError(
                        f"Found valid answer '{answer}' but it's not in options list {options}. "
                        f"This shouldn't happen - the scorer marked it valid but it doesn't match "
                        f"any option. Group key: {key}"
                    )
                response_dist[answer] += 1
        
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
    
    return output_data
