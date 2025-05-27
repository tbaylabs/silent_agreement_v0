from typing import Dict

def group_results_generator(grouped_data: Dict[str, Dict]) -> Dict:
    """Generate group_results.json from grouped scores data."""
    output_data = {}
    for key, group in grouped_data.items():
        # Create response distribution with all values set to 0
        options = group["options_list"]
        response_dist = {option: 0 for option in options}
        
        # Track invalid counts separately (not in response distribution)
        invalid_illegible_count = 0
        invalid_ooc_count = 0
        
        # Count responses and collect token counts
        token_counts = []
        ooc_warning_count = 0
        
        for sample_score in group["scores"]:
            score = sample_score.score if hasattr(sample_score, 'score') else sample_score.scores
            
            # Collect token count from score metadata
            token_count = score.metadata.get("token_count", 0) if score.metadata else 0
            token_counts.append(token_count)
            
            # Check OOC validity
            ooc_validity = score.metadata.get("ooc_validity", "not_applicable") if score.metadata else "not_applicable"
            
            if score.value == 0:
                # Check if it's an OOC violation or illegible
                if score.answer == "invalid_ooc":
                    invalid_ooc_count += 1
                else:
                    # This is an illegible response (failed extraction)
                    invalid_illegible_count += 1
            else:
                # Valid answer extracted
                answer = score.answer
                if answer not in options:
                    raise ValueError(
                        f"Found valid answer '{answer}' but it's not in options list {options}. "
                        f"This shouldn't happen - the scorer marked it valid but it doesn't match "
                        f"any option. Group key: {key}"
                    )
                response_dist[answer] += 1
                
                # Track OOC warnings (valid responses with warnings)
                if ooc_validity == "warning":
                    ooc_warning_count += 1
        
        
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
        
        # Calculate validity statistics
        total_count = len(group["scores"])
        total_invalid_count = invalid_illegible_count + invalid_ooc_count
        
        validity_stats = {
            "illegible_invalid_count": invalid_illegible_count,
            "ooc_invalid_count": invalid_ooc_count,
            "ooc_warning_count": ooc_warning_count,
            "total_invalid_count": total_invalid_count,
            "total_invalid_rate": round(total_invalid_count / total_count, 3) if total_count > 0 else 0
        }
        
        output_data[key] = {
            "option_id": group["option_id"],
            "options_list": group["options_list"],
            "option_name": group["option_name"],
            "option_type": group["option_type"],
            "condition": group["condition"],
            "score_count": total_count,
            "response_distribution": response_dist,
            "validity_stats": validity_stats,
            "token_stats": token_stats
        }
    
    return output_data
