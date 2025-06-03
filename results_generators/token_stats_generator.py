"""Generate token statistics from evaluation results."""

import json
import statistics
from typing import Dict, List, Any, Optional
import uuid
from collections import defaultdict


def get_condition_names(eval_type: str) -> Dict[str, str]:
    """Map internal condition names to output names based on eval type."""
    if eval_type == "base":
        return {
            "control": "control",
            "ooc_coordinate": "ooc_coordinate",
            "cot_coordinate": "cot_coordinate"
        }
    else:  # reasoning (both effort and tokens)
        return {
            "control": "control",
            "coordinate_only": "coordinate_only",
            "coordinate_elicit_thought": "coordinate_elicit_thought"
        }


def calculate_stats(values: List[float]) -> Dict[str, float]:
    """Calculate average, median, high, and low from a list of values."""
    if not values:
        return {
            "average": 0,
            "median": 0,
            "high": 0,
            "low": 0
        }
    
    return {
        "average": round(statistics.mean(values), 1),
        "median": round(statistics.median(values), 1),
        "high": round(max(values), 1),
        "low": round(min(values), 1)
    }


def generate_token_stats(samples: List[Dict[str, Any]], eval_type: str = "base") -> Dict[str, Any]:
    """
    Generate token statistics from evaluation samples.
    
    Args:
        samples: List of sample dictionaries from the evaluation
        eval_type: Type of evaluation ("base" or "reasoning")
    
    Returns:
        Dictionary with token statistics structured as requested
    """
    # Get condition name mapping
    condition_map = get_condition_names(eval_type)
    
    # Initialize data structures
    tokens_by_condition = defaultdict(list)
    tokens_by_condition_and_option = defaultdict(lambda: defaultdict(list))
    
    # Process each sample
    for sample in samples:
        # Get metadata
        condition_internal = sample.get("metadata", {}).get("condition", "")
        option_id = sample.get("metadata", {}).get("option_id", "")
        
        # Map internal condition name to output name
        condition = condition_map.get(condition_internal, condition_internal)
        if not condition:
            continue
        
        # Get output token counts (including reasoning tokens for reasoning models)
        tokens = None
        
        # First try: direct token fields
        if "output_tokens" in sample:
            output_tokens = sample.get("output_tokens", 0) or 0
            reasoning_tokens = sample.get("reasoning_tokens", 0) or 0
            tokens = output_tokens + reasoning_tokens
        
        # Second try: from model_usage
        elif "model_usage" in sample:
            usage = sample["model_usage"]
            if isinstance(usage, dict):
                output_tokens = usage.get("output_tokens", 0) or 0
                reasoning_tokens = usage.get("reasoning_tokens", 0) or 0
                tokens = output_tokens + reasoning_tokens
        
        # Third try: from usage field
        elif "usage" in sample:
            usage = sample["usage"]
            if isinstance(usage, dict):
                output_tokens = usage.get("output_tokens", 0) or 0
                reasoning_tokens = usage.get("reasoning_tokens", 0) or 0
                tokens = output_tokens + reasoning_tokens
        
        # Skip if no token data found
        if tokens is None or tokens == 0:
            continue
        
        # Add to collections
        tokens_by_condition[condition].append(tokens)
        tokens_by_condition_and_option[condition][option_id].append(tokens)
    
    # Calculate statistics
    result = {
        "token_stats": {
            "by_condition": {},
            "by_condition_and_option": {}
        },
        "_notice": f"This file contains LLM evaluation and benchmark data. Please avoid accidentally training models on this file. CANARY GUID: {str(uuid.uuid4())}"
    }
    
    # Stats by condition
    for condition in condition_map.values():
        if condition in tokens_by_condition:
            result["token_stats"]["by_condition"][condition] = calculate_stats(
                tokens_by_condition[condition]
            )
    
    # Stats by condition and option
    for condition in condition_map.values():
        if condition in tokens_by_condition_and_option:
            result["token_stats"]["by_condition_and_option"][condition] = {}
            
            # Sort options for consistent output
            sorted_options = sorted(tokens_by_condition_and_option[condition].keys())
            
            for option_id in sorted_options:
                token_values = tokens_by_condition_and_option[condition][option_id]
                if token_values:
                    result["token_stats"]["by_condition_and_option"][condition][option_id] = calculate_stats(token_values)
    
    return result


def generate_token_stats_from_eval(eval_file_path: str, eval_type: str = "base") -> Optional[Dict[str, Any]]:
    """
    Generate token statistics from an evaluation file.
    
    Args:
        eval_file_path: Path to the .eval file
        eval_type: Type of evaluation to determine condition names
    
    Returns:
        Token statistics dictionary or None if generation fails
    """
    try:
        from inspect_ai.log import read_eval_log
        
        # Load the eval file using inspect_ai
        log = read_eval_log(eval_file_path)
        
        if not log.samples:
            print(f"Warning: No samples found in {eval_file_path}")
            return None
        
        # Convert samples to dictionary format for processing
        samples_data = []
        for sample in log.samples:
            sample_dict = {
                "metadata": sample.metadata,
                "model_usage": {}
            }
            
            # Extract token usage from model_usage
            if hasattr(sample, 'model_usage') and sample.model_usage:
                for model_name, usage in sample.model_usage.items():
                    if hasattr(usage, 'output_tokens'):
                        output_tokens = usage.output_tokens or 0
                        reasoning_tokens = getattr(usage, 'reasoning_tokens', None) or 0
                        sample_dict["model_usage"] = {
                            "output_tokens": output_tokens,
                            "reasoning_tokens": reasoning_tokens
                        }
                        break  # Use first model's usage
            
            samples_data.append(sample_dict)
        
        # Generate stats
        return generate_token_stats(samples_data, eval_type)
        
    except Exception as e:
        print(f"Error generating token stats from {eval_file_path}: {e}")
        return None