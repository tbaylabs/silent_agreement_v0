from inspect_ai.scorer import metric, Metric, SampleScore
from typing import Dict
import json
from group_results_generator import group_results_generator
from options_results_generator import generate_options_results

@metric 
def condition_scores() -> Metric:
    """Returns scores for each condition-option_id combination."""
    def metric_func(scores: list[SampleScore]) -> Dict[str, float]:
        # Load options lists
        options_file = "dataset_generation/options_lists/options_lists_v0.json"
        with open(options_file) as f:
            options_lists = json.load(f)

        # Group scores by condition-option_id combination with metadata
        grouped_scores: Dict[str, Dict] = {}
        for sample in scores:
            option_id = sample.sample_metadata["option_id"]
            condition = sample.sample_metadata["condition"]
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
            
            grouped_scores[key]["scores"].append(sample)
            
        # Print options list for each group
        print("group score keys:")
        for key in grouped_scores:
            print(key)
            
        # Generate all results files
        group_results = group_results_generator(grouped_scores)
        options_results = generate_options_results(group_results)
        generate_stats_overview(options_results)
        
        # Count samples for each combination
        results = {
            key: float(len(group["scores"]))
            for key, group in grouped_scores.items()
        }
            
        return results
    return metric_func
