"""Main stats overview generator using modular components."""
from typing import Dict, Any, List
from .experiment_config import BASE_CONFIG, REASONING_CONFIG
from .validation_utils import validate_data
from .value_collection import collect_values, build_output
from .experiment_runner import run_experiments


def detect_available_conditions(options_results: Dict[str, Any]) -> List[str]:
    """Detect which conditions are available in the data."""
    all_conditions = set()
    for option_data in options_results.values():
        if isinstance(option_data, dict) and "trial_blocks_by_condition" in option_data:
            all_conditions.update(option_data["trial_blocks_by_condition"].keys())
    return list(all_conditions)


def generate_stats_overview(
    options_results: Dict[str, Any],
    is_reasoning_eval: bool = False,
    eval_type: str = "base"
) -> Dict[str, Any]:
    """
    Generate overview statistics across all options.
    
    Args:
        options_results: Dictionary of option results from options_results_generator
        is_reasoning_eval: Whether this is a reasoning evaluation
        eval_type: Type of reasoning eval ("token" or "effort") - unused now since both are the same
        
    Returns:
        Dict containing experiments, absolute_metrics, and experiment_validity
        Returns None if validation fails
    """
    # Select configuration based on eval type
    config = REASONING_CONFIG if is_reasoning_eval else BASE_CONFIG
    
    # Step 1: Validate data
    validation = validate_data(options_results, config)
    if not validation.is_valid:
        return None
    
    # Step 2: Collect values for analysis
    value_collectors = collect_values(
        options_results, 
        config, 
        validation.invalid_measures,
        is_reasoning_eval
    )
    
    # Step 3: Run experiments
    experiment_results = run_experiments(
        value_collectors.experiment_values,
        validation.invalid_measures,
        validation.total_measures,
        config
    )
    
    # Step 4: Build output
    return build_output(experiment_results, value_collectors, config)