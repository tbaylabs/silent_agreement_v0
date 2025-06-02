"""Value collection utilities for statistical analysis."""
from typing import Dict, Any, List, NamedTuple
from .experiment_config import EvaluationConfig
from .statistical_utils import calculate_stats


class ValueCollectors(NamedTuple):
    """Collected values for statistical analysis."""
    experiment_values: Dict[str, Dict[str, List[float]]]  # For experiments: exp1, exp2, exp3
    absolute_metrics: Dict[str, Dict[str, Dict[str, List[float]]]]  # For absolute stats
    validity_info: Dict[str, Any]  # Counts and other validity tracking


def collect_values(
    options_results: Dict[str, Any],
    config: EvaluationConfig,
    invalid_measures: Dict[str, List[str]],
    is_reasoning_eval: bool = False
) -> ValueCollectors:
    """
    Collect values using generic experiment names internally.
    
    Args:
        options_results: Raw options results data
        config: Evaluation configuration
        invalid_measures: Invalid measures from validation
        is_reasoning_eval: Whether this is a reasoning evaluation
        
    Returns:
        ValueCollectors with all collected data
    """
    metrics = ["top_prop_exclude_invalid", "top_prop_include_invalid"]
    
    # Initialize collectors
    absolute_metrics = _initialize_absolute_metrics(metrics, config.conditions)
    experiment_values = _initialize_experiment_values()
    validity_info = _initialize_validity_info(config.conditions, is_reasoning_eval)
    
    # Collect values from each option
    for option_id, option_data in options_results.items():
        if option_id == "_notice":
            continue
            
        if not _has_all_conditions(option_data, config.conditions):
            continue
            
        option_type = option_data["options_type"]
        
        # Collect absolute metrics
        _collect_absolute_metrics(
            option_data, absolute_metrics, metrics, config.conditions, option_type
        )
        
        # Collect experiment difference values
        _collect_experiment_values(
            option_data, experiment_values, config, invalid_measures, option_id, option_type
        )
        
        # Collect validity information
        _collect_validity_info(
            option_data, validity_info, config.conditions, is_reasoning_eval
        )
    
    return ValueCollectors(
        experiment_values=experiment_values,
        absolute_metrics=absolute_metrics,
        validity_info=validity_info
    )


def _initialize_absolute_metrics(
    metrics: List[str], 
    conditions: List[str]
) -> Dict[str, Dict[str, Dict[str, List[float]]]]:
    """Initialize structure for absolute metrics collection."""
    return {
        metric: {
            cond: {"all": [], "symbol": [], "text": []} 
            for cond in conditions
        }
        for metric in metrics
    }


def _initialize_experiment_values() -> Dict[str, Dict[str, List[float]]]:
    """Initialize structure for experiment values."""
    return {
        "exp1": {"symbol_and_text": [], "symbol": [], "text": []},
        "exp2": {"symbol_and_text": [], "symbol": [], "text": []},
        "exp3": {"symbol_and_text": [], "symbol": [], "text": []}
    }


def _initialize_validity_info(
    conditions: List[str], 
    is_reasoning_eval: bool
) -> Dict[str, Any]:
    """Initialize validity tracking structures."""
    validity_info = {
        "totals": {
            "total": {cond: 0 for cond in conditions},
            "valid": {cond: 0 for cond in conditions},
            "illegible_invalid": {cond: 0 for cond in conditions},
            "combined_invalid": {cond: 0 for cond in conditions}
        }
    }
    
    # Only track OOC-specific metrics for base evaluations
    if not is_reasoning_eval:
        validity_info["totals"]["ooc_invalid"] = {cond: 0 for cond in conditions}
        validity_info["totals"]["ooc_warning_valid"] = {cond: 0 for cond in conditions}
    
    return validity_info


def _has_all_conditions(option_data: Dict[str, Any], conditions: List[str]) -> bool:
    """Check if option has all required conditions."""
    trial_blocks = option_data.get("trial_blocks_by_condition", {})
    return all(cond in trial_blocks for cond in conditions)


def _collect_absolute_metrics(
    option_data: Dict[str, Any],
    absolute_metrics: Dict[str, Dict[str, Dict[str, List[float]]]],
    metrics: List[str],
    conditions: List[str],
    option_type: str
) -> None:
    """Collect absolute metric values."""
    trial_blocks = option_data["trial_blocks_by_condition"]
    
    for metric in metrics:
        for condition in conditions:
            if condition in trial_blocks:
                val = trial_blocks[condition]["stats"][metric]
                absolute_metrics[metric][condition]["all"].append(val)
                absolute_metrics[metric][condition][option_type].append(val)


def _collect_experiment_values(
    option_data: Dict[str, Any],
    experiment_values: Dict[str, Dict[str, List[float]]],
    config: EvaluationConfig,
    invalid_measures: Dict[str, List[str]],
    option_id: str,
    option_type: str
) -> None:
    """Collect difference values for experiments."""
    differences = option_data.get("top_prop_exclude_invalid_differences", {})
    if not differences:
        return
    
    # Experiment 1: treatment1 vs control
    if config.difference_keys[0] in differences:
        if option_id not in invalid_measures["experiment_1"]:
            val = differences[config.difference_keys[0]]
            experiment_values["exp1"]["symbol_and_text"].append(val)
            experiment_values["exp1"][option_type].append(val)
    
    # Experiment 2: treatment2 vs control
    if config.difference_keys[1] in differences:
        if option_id not in invalid_measures["experiment_2"]:
            val = differences[config.difference_keys[1]]
            experiment_values["exp2"]["symbol_and_text"].append(val)
            experiment_values["exp2"][option_type].append(val)
    
    # Experiment 3: treatment2 vs treatment1
    if config.difference_keys[2] in differences:
        if (option_id not in invalid_measures["experiment_1"] and 
            option_id not in invalid_measures["experiment_2"]):
            val = differences[config.difference_keys[2]]
            experiment_values["exp3"]["symbol_and_text"].append(val)
            experiment_values["exp3"][option_type].append(val)


def _collect_validity_info(
    option_data: Dict[str, Any],
    validity_info: Dict[str, Any],
    conditions: List[str],
    is_reasoning_eval: bool
) -> None:
    """Collect validity counts and metrics."""
    for condition in conditions:
        condition_stats = option_data["trial_blocks_by_condition"][condition]["stats"]
        response_dist = option_data["trial_blocks_by_condition"][condition]["response_distribution"]
        
        total_count = condition_stats["total_response_count"]
        valid_count = condition_stats.get("valid_count", 0)
        illegible_invalid = response_dist.get("illegible_invalid_count", 0)
        
        validity_info["totals"]["total"][condition] += total_count
        validity_info["totals"]["valid"][condition] += valid_count
        validity_info["totals"]["illegible_invalid"][condition] += illegible_invalid
        
        if is_reasoning_eval:
            # For reasoning evals, only track illegible invalids
            total_invalid = condition_stats.get("total_invalid_count", illegible_invalid)
            validity_info["totals"]["combined_invalid"][condition] += total_invalid
        else:
            # For base evals, track all invalid types
            ooc_invalid = response_dist.get("ooc_invalid_count", 0)
            ooc_warning = condition_stats.get("ooc_warning_valid_count", 0)
            total_invalid = condition_stats.get("total_invalid_count", illegible_invalid + ooc_invalid)
            
            validity_info["totals"]["ooc_invalid"][condition] += ooc_invalid
            validity_info["totals"]["ooc_warning_valid"][condition] += ooc_warning
            validity_info["totals"]["combined_invalid"][condition] += total_invalid


def build_output(
    experiment_results: Dict[str, Any],
    value_collectors: ValueCollectors,
    config: EvaluationConfig
) -> Dict[str, Any]:
    """Build the final output format."""
    metrics = ["top_prop_exclude_invalid", "top_prop_include_invalid"]
    
    # Build absolute metrics
    absolute_metrics = {}
    for metric in metrics:
        absolute_metrics[metric] = {
            "symbol_and_text": {
                f"{cond}_stats": calculate_stats(value_collectors.absolute_metrics[metric][cond]["all"]) 
                for cond in config.conditions
            },
            "symbol": {
                f"{cond}_stats": calculate_stats(value_collectors.absolute_metrics[metric][cond]["symbol"]) 
                for cond in config.conditions
            },
            "text": {
                f"{cond}_stats": calculate_stats(value_collectors.absolute_metrics[metric][cond]["text"]) 
                for cond in config.conditions
            }
        }
    
    return {
        "experiments": experiment_results["experiment_results"],
        "absolute_metrics": absolute_metrics,
        "experiment_validity": experiment_results["experiment_validity"]
    }