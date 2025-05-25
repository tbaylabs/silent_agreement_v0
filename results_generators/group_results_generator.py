from typing import Dict

def group_results_generator(grouped_data: Dict[str, Dict]) -> Dict:
    """Generate group_results.json from grouped scores data."""
    output_data = {}
    for key, group in grouped_data.items():
        # Create response distribution with all values set to 0
        options = group["options_list"]
        response_dist = {option: 0 for option in options}
        response_dist["invalid"] = 0  # Add invalid category
        response_dist["fail_subset_invalid"] = 0  # Add fail subcategory
        
        # Count responses and collect token counts
        token_counts = []
        for sample_score in group["scores"]:
            score = sample_score.score
            
            # Collect token count from score metadata
            token_count = score.metadata.get("token_count", 0) if score.metadata else 0
            token_counts.append(token_count)
            
            if score.value == 0:
                response_dist["invalid"] += 1
                if score.answer == "fail":
                    response_dist["fail_subset_invalid"] += 1
            else:
                answer = score.answer
                if answer not in options:
                    raise ValueError(
                        f"Found valid answer '{answer}' but it's not in options list {options}. "
                        f"This shouldn't happen - the scorer marked it valid but it doesn't match "
                        f"any option. Group key: {key}"
                    )
                response_dist[answer] += 1
        
        # Calculate token statistics for this group
        import numpy as np
        token_stats = {}
        if token_counts:
            token_stats = {
                "mean": round(float(np.mean(token_counts)), 3),
                "median": round(float(np.median(token_counts)), 3),
                "q1": round(float(np.percentile(token_counts, 25)), 3),
                "q3": round(float(np.percentile(token_counts, 75)), 3),
                "min": int(min(token_counts)),
                "max": int(max(token_counts)),
                "total_tokens": int(sum(token_counts))
            }
        
        output_data[key] = {
            "option_id": group["option_id"],
            "options_list": group["options_list"],
            "option_name": group["option_name"],
            "option_type": group["option_type"],
            "condition": group["condition"],
            "score_count": len(group["scores"]),
            "response_distribution": response_dist,
            "token_stats": token_stats
        }
    
    return output_data
