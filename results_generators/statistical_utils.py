"""Statistical utility functions."""
from typing import Dict, Any, List
import numpy as np
from scipy import stats
from utils import SIGNIFICANCE_LEVEL


def calculate_stats(values: List[float]) -> Dict[str, float]:
    """Calculate mean and standard deviation."""
    if not values:
        return {
            "mean": None,
            "sd": None,
        }
    
    mean = np.mean(values)
    sd = np.std(values, ddof=1) if len(values) > 1 else 0  # ddof=1 for sample standard deviation
    
    return {
        "mean": round(float(mean), 3),
        "sd": round(float(sd), 3),
    }


def calculate_one_sample_ttest(values: List[float]) -> Dict[str, Any]:
    """
    Perform a one-sided t-test for H₁: mean > 0.
    Returns statistics including one-tailed p-value and CI lower bound.
    The result is considered significant if one_tail_p_value < SIGNIFICANCE_LEVEL and one_tail_ci_95_lower > 0.
    """
    if not values:
        return {
            "mean": None,
            "one_tail_significant": None,
            "one_tail_ci_95_lower": None,
            "one_tail_p_value": None,
            "one_tail_t_stat": None
        }
    
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

    significant = (p_value < SIGNIFICANCE_LEVEL) and (ci_lower is not None and ci_lower > 0)

    return {
        "mean": round(float(mean), 3),
        "one_tail_significant": significant,
        "one_tail_ci_95_lower": round(float(ci_lower), 3) if ci_lower is not None else None,
        "one_tail_p_value": f"{p_value:.4f}",
        "one_tail_t_stat": round(float(t_stat), 3)
    }


def create_nan_result() -> Dict[str, Any]:
    """Create a placeholder result for experiments that weren't run."""
    return {
        "mean": None,
        "sd": None,
        "one_tail_significant": None,
        "one_tail_ci_95_lower": None,
        "one_tail_p_value": None,
        "one_tail_t_stat": None
    }