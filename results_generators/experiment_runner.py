"""Generic experiment runner that works for all evaluation types."""
from typing import Dict, Any, List
from utils import INVALID_THRESHOLD
from .experiment_config import EvaluationConfig
from .statistical_utils import calculate_stats, calculate_one_sample_ttest, create_nan_result


def run_experiments(
    experiment_values: Dict[str, Dict[str, List[float]]],
    invalid_measures: Dict[str, List[str]], 
    total_measures: int,
    config: EvaluationConfig
) -> Dict[str, Any]:
    """
    Run all 3 experiments using generic logic.
    
    Args:
        experiment_values: Dict with keys "exp1", "exp2", "exp3" containing values
        invalid_measures: Dict tracking invalid measures for each experiment
        total_measures: Total number of measures
        config: Evaluation configuration
        
    Returns:
        Dict containing experiment results and validity information
    """
    # Check validity for experiments 1 and 2
    exp1_valid = _is_experiment_valid(invalid_measures["experiment_1"], total_measures)
    exp2_valid = _is_experiment_valid(invalid_measures["experiment_2"], total_measures)
    
    # Run 3 experiments
    experiment_results = {}
    
    # Experiment 1: treatment1 vs control
    if exp1_valid:
        experiment_results[config.experiment_names[0]] = run_single_experiment(
            experiment_values["exp1"]
        )
    else:
        experiment_results[config.experiment_names[0]] = _create_nan_experiment_results()
    
    # Experiment 2: treatment2 vs control
    if exp2_valid:
        experiment_results[config.experiment_names[1]] = run_single_experiment(
            experiment_values["exp2"]
        )
    else:
        experiment_results[config.experiment_names[1]] = _create_nan_experiment_results()
    
    # Experiment 3: treatment2 vs treatment1 (only if both are valid)
    if exp1_valid and exp2_valid:
        experiment_results[config.experiment_names[2]] = run_single_experiment(
            experiment_values["exp3"]
        )
    else:
        experiment_results[config.experiment_names[2]] = _create_nan_experiment_results()
    
    # Build validity information
    experiment_validity = _build_validity_info(
        invalid_measures, exp1_valid, exp2_valid, total_measures
    )
    
    return {
        "experiment_results": experiment_results,
        "experiment_validity": experiment_validity
    }


def run_single_experiment(difference_values: Dict[str, List[float]]) -> Dict[str, Dict[str, Any]]:
    """Run statistical analysis for a single experiment."""
    results = {}
    
    for category in ["symbol_and_text", "symbol", "text"]:
        values = difference_values.get(category, [])
        if values:
            stats_result = calculate_stats(values)
            ttest_result = calculate_one_sample_ttest(values)
            results[category] = {**stats_result, **ttest_result}
        else:
            results[category] = create_nan_result()
    
    return results


def _is_experiment_valid(invalid_list: List[str], total_measures: int) -> bool:
    """Check if an experiment meets the validity threshold."""
    if total_measures == 0:
        return False
    return len(invalid_list) / total_measures <= INVALID_THRESHOLD


def _create_nan_experiment_results() -> Dict[str, Dict[str, Any]]:
    """Create nan results for all categories."""
    return {
        "symbol_and_text": create_nan_result(),
        "symbol": create_nan_result(),
        "text": create_nan_result()
    }


def _build_validity_info(
    invalid_measures: Dict[str, List[str]],
    exp1_valid: bool,
    exp2_valid: bool,
    total_measures: int
) -> Dict[str, Any]:
    """Build experiment validity information."""
    all_measures_valid = (
        len(invalid_measures["all_invalid"]) == 0 and 
        len(invalid_measures["experiment_1"]) == 0 and 
        len(invalid_measures["experiment_2"]) == 0
    )
    
    return {
        "invalid_measures": {
            "experiment_1": invalid_measures["experiment_1"],
            "experiment_2": invalid_measures["experiment_2"],
            "all_experiments": invalid_measures["all_invalid"]
        },
        "experiment_valid": {
            "experiment_1": exp1_valid,
            "experiment_2": exp2_valid,
            "all_measures_valid": all_measures_valid
        },
        "total_measures": total_measures,
        "invalid_threshold": INVALID_THRESHOLD
    }