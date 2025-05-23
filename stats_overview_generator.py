from typing import Dict, Any
import json
import numpy as np
from scipy import stats

def calculate_stats(values: list[float]) -> Dict[str, float]:
    """Calculate mean and standard deviation."""
    mean = np.mean(values)
    sd = np.std(values, ddof=1) if len(values) > 1 else 0  # ddof=1 for sample standard deviation
    
    return {
        "mean": round(mean, 3),
        "sd": round(sd, 3),
    }

def calculate_token_stats(token_stats_list: list[Dict]) -> Dict[str, float]:
    """Calculate aggregated token statistics from a list of token stat dictionaries."""
    if not token_stats_list:
        return {}
    
    # Collect all values for each metric
    means = [stats.get("mean", 0) for stats in token_stats_list if stats]
    medians = [stats.get("median", 0) for stats in token_stats_list if stats]
    q1s = [stats.get("q1", 0) for stats in token_stats_list if stats]
    q3s = [stats.get("q3", 0) for stats in token_stats_list if stats]
    mins = [stats.get("min", 0) for stats in token_stats_list if stats]
    maxs = [stats.get("max", 0) for stats in token_stats_list if stats]
    
    if not means:  # No valid data
        return {}
    
    return {
        "mean": round(np.mean(means), 3),
        "median": round(np.median(medians), 3),
        "q1": round(np.median(q1s), 3),
        "q3": round(np.median(q3s), 3),
        "min": int(min(mins)),
        "max": int(max(maxs)),
        "range": [int(min(mins)), int(max(maxs))]
    }

def calculate_one_sample_ttest(values: list[float]) -> Dict[str, Any]:
    """
    Perform a one-sided t-test for H₁: mean > 0.
    Returns statistics including one-tailed p-value and CI lower bound.
    The result is considered significant if one_tail_p_value < 0.05 and one_tail_ci_95_lower > 0.
    """
    mean = np.mean(values)
    n = len(values)
    if n > 1:
        sd = np.std(values, ddof=1)
        se = sd / np.sqrt(n)
    else:
        se = 0

    # compute t-statistic manually
    t_stat = mean / se if se != 0 else 0

    # one-sided p-value for H₁: mean > 0:
    # If the mean is not above 0, we set p-value to 1.
    if mean > 0 and se != 0:
        p_value = stats.t.sf(t_stat, df=n-1) 
    else:
        p_value = 1.0

    # For a one-sided 95% confidence interval (lower bound only):
    # t.ppf(0.95, df) gives the appropriate t-critical value.
    if n > 1 and se != 0:
        t_crit = stats.t.ppf(0.95, df=n-1)
        ci_lower = mean - t_crit * se
    else:
        ci_lower = None

    # Since the test is one-sided (only interested if mean > 0), there's no finite upper bound.
    ci_upper = None

    significant = (p_value < 0.05) and (ci_lower is not None and ci_lower > 0)

    return {
        "mean": round(mean, 3),
        "one_tail_significant": significant,
        "one_tail_ci_95_lower": round(ci_lower, 3) if ci_lower is not None else None,
        "one_tail_p_value": f"{p_value:.4f}",
        "one_tail_t_stat": round(t_stat, 3)
    }

def generate_stats_overview(options_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate overview statistics across all options.
    Returns stats overview dict and writes results to stats_overview.json 
    only if all data meets validity criteria.
    """
    # Validate data before proceeding
    for option_data in options_results.values():
        # Check if differences exists and is not empty
        if not option_data.get("differences"):
            print("Skipping stats overview generation: some options missing differences data")
            return None
            
        # Check if all conditions have valid response counts
        for condition_data in option_data["conditions"].values():
            if condition_data["trial_block_stats"]["total_response_count"] < 1:
                print("Skipping stats overview generation: some conditions have no responses")
                return None

    # Initialize accumulators for each metric and condition
    metrics = ["top_prop_include_invalid", "top_prop_exclude_invalid"]
    conditions = ["control_suppress_cot", "coordinate_suppress_cot", "coordinate_elicit_cot"]
    diff_pairs = [
        "coordinate_suppress_cot_vs_control",
        "coordinate_elicit_cot_vs_control",
        "coordinate_elicit_cot_vs_suppress_cot"
    ]
    
    # Initialize data collectors for calculating SDs
    value_collectors = {
        "absolute_metrics": {
            metric: {cond: {"all": [], "symbol": [], "text": []} for cond in conditions}
            for metric in metrics
        },
        "difference_metrics": {
            metric: {pair: {"all": [], "symbol": [], "text": []} for pair in diff_pairs}
            for metric in metrics
        }
    }
    
    # Initialize validity metrics collectors
    validity_collectors = {
        "total_count": {cond: [] for cond in conditions},
        "valid_count": {
            cond: {"values": [], "options_lists": []} for cond in conditions
        },
        "token_count": {
            cond: [] for cond in conditions
        }
    }
    
    totals = {
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
            
            option_type = option_data["options_type"]  # "symbol" or "text"
            for metric in metrics:
                for condition in conditions:
                    val = overview[metric][condition]
                    value_collectors["absolute_metrics"][metric][condition]["all"].append(val)
                    value_collectors["absolute_metrics"][metric][condition][option_type].append(val)
            for metric in metrics:
                for pair in diff_pairs:
                    val = differences[metric][pair]
                    value_collectors["difference_metrics"][metric][pair]["all"].append(val)
                    value_collectors["difference_metrics"][metric][pair][option_type].append(val)
            
            # Sum counts and collect validity metrics
            for condition in conditions:
                condition_data = option_data["conditions"][condition]["trial_block_stats"]
                total_count = condition_data["total_response_count"]
                valid_count = condition_data["valid_response_count"]
                
                totals["counts"]["total"][condition] += total_count
                totals["counts"]["valid"][condition] += valid_count
                
                validity_collectors["total_count"][condition].append(total_count)
                validity_collectors["valid_count"][condition]["values"].append(valid_count)
                validity_collectors["valid_count"][condition]["options_lists"].append(option_data["options_list"])
                
                # Collect token stats
                token_stats = option_data["conditions"][condition].get("token_stats", {})
                if token_stats:
                    validity_collectors["token_count"][condition].append(token_stats)
    
    # Calculate stats
    stats_overview = {
        "meta": {
            "total_count": option_count,
            "total_invalid_count": sum(totals["counts"]["total"][cond] - totals["counts"]["valid"][cond] for cond in conditions),
            "total_valid_count": sum(totals["counts"]["valid"][cond] for cond in conditions)
        },
        "difference_metrics": {
            metric: {
                "all": {
                    pair: {
                        **calculate_stats(value_collectors["difference_metrics"][metric][pair]["all"]),
                        **calculate_one_sample_ttest(value_collectors["difference_metrics"][metric][pair]["all"])
                    }
                    for pair in diff_pairs
                },
                "symbol": {
                    pair: {
                        **calculate_stats(value_collectors["difference_metrics"][metric][pair]["symbol"]),
                        **calculate_one_sample_ttest(value_collectors["difference_metrics"][metric][pair]["symbol"])
                    }
                    for pair in diff_pairs
                },
                "text": {
                    pair: {
                        **calculate_stats(value_collectors["difference_metrics"][metric][pair]["text"]),
                        **calculate_one_sample_ttest(value_collectors["difference_metrics"][metric][pair]["text"])
                    }
                    for pair in diff_pairs
                }
            }
            for metric in metrics
        },
        "absolute_metrics": {
            metric: {
                "all": { f"{cond}_stats": calculate_stats(value_collectors["absolute_metrics"][metric][cond]["all"]) for cond in conditions },
                "symbol": { f"{cond}_stats": calculate_stats(value_collectors["absolute_metrics"][metric][cond]["symbol"]) for cond in conditions },
                "text": { f"{cond}_stats": calculate_stats(value_collectors["absolute_metrics"][metric][cond]["text"]) for cond in conditions }
            }
            for metric in metrics
        },
        "validity_metrics": {
            "sample_count": {
                "total_count": {
                    f"{cond}_stats": {
                        "mean": round(np.mean(validity_collectors["total_count"][cond]), 3),
                        "highest": round(max(validity_collectors["total_count"][cond]), 3),
                        "lowest": round(min(validity_collectors["total_count"][cond]), 3)
                    }
                    for cond in conditions
                },
                "valid_count": {
                    f"{cond}_stats": {
                        "mean": round(np.mean(validity_collectors["valid_count"][cond]["values"]), 3),
                        "highest": round(max(validity_collectors["valid_count"][cond]["values"]), 3),
                        "lowest": round(min(validity_collectors["valid_count"][cond]["values"]), 3),
                        "lowest_list": validity_collectors["valid_count"][cond]["options_lists"][
                            validity_collectors["valid_count"][cond]["values"].index(
                                min(validity_collectors["valid_count"][cond]["values"])
                            )
                        ]
                    }
                    for cond in conditions
                }
            },
            "token_count": {
                "all": calculate_token_stats([
                    stats for cond in conditions 
                    for stats in validity_collectors["token_count"][cond]
                ]),
                **{
                    f"{cond}_stats": calculate_token_stats(validity_collectors["token_count"][cond])
                    for cond in conditions
                }
            }
        }
    }
    
    # Write to file
    with open("stats_overview.json", "w", encoding='utf-8') as f:
        json.dump(
            stats_overview,
            f,
            indent=2,
            ensure_ascii=False,
            default=lambda o: o.item() if hasattr(o, "item") else o
        )
        
    return stats_overview
