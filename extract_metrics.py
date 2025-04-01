#!/usr/bin/env python3
import json
import os
import glob
import re
import matplotlib.pyplot as plt
import numpy as np
from math import sqrt

def extract_model_name(path):
    # Extract model name from path like results/claude-3-5-sonnet-20241022/20250222_140448/stats_overview.json
    parts = path.split(os.sep)
    if len(parts) >= 2:
        return parts[-3]  # Get the model name folder
    return "unknown"

def calculate_upper_ci(mean, sd, n=20, confidence=0.95):
    """Calculate upper confidence interval given a lower CI value"""
    # Using t-distribution with n-1 degrees of freedom
    # For 95% CI and 19 degrees of freedom, the t-value is approximately 1.729
    t_value = 1.729  # For 95% CI with df=19
    # The full width of the CI is 2 * t * (sd / sqrt(n))
    ci_width = 2 * t_value * (sd / sqrt(n))
    # Upper bound = mean + half the CI width
    return mean + (ci_width / 2)

def create_difference_metric_graph(results, metric_key, output_filename, is_elicit=False):
    """Create a graph for a specific difference metric"""
    # Extract model names and mean values for 'all' category of the specified metric
    model_data = []
    
    for model_name, data in results.items():
        if "difference_metrics" in data and "all" in data["difference_metrics"]:
            if metric_key in data["difference_metrics"]["all"]:
                metric = data["difference_metrics"]["all"][metric_key]
                mean = metric.get("mean", 0)
                sd = metric.get("sd", 0)
                lower_ci = metric.get("one_tail_ci_95_lower", mean - 0.1)
                upper_ci = calculate_upper_ci(mean, sd)
                
                model_data.append({
                    "model": model_name,
                    "mean": mean,
                    "lower_ci": lower_ci,
                    "upper_ci": upper_ci
                })
    
    # Sort models by mean value
    model_data.sort(key=lambda x: x["mean"])
    
    # Prepare data for plotting
    models = [item["model"] for item in model_data]
    means = [item["mean"] for item in model_data]
    lower_errors = [item["mean"] - item["lower_ci"] for item in model_data]
    upper_errors = [item["upper_ci"] - item["mean"] for item in model_data]
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    
    # Create bars with error bars
    plt.errorbar(
        models, means, 
        yerr=[lower_errors, upper_errors],
        fmt='o', 
        capsize=5, 
        ecolor='black',
        markersize=8, 
        color='skyblue'
    )
    
    # Add horizontal line at y=0
    plt.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
    
    # Set title and labels based on which metric we're showing
    if is_elicit:
        title = "Change in Performance: Coordination with Elicited Chain-of-Thought vs Control"
        subtitle = "(Positive values indicate improved convergence on top response)"
    else:
        title = "Change in Performance: Coordination with Suppressed Chain-of-Thought vs Control"
        subtitle = "(Positive values indicate improved convergence on top response)"
    
    # Customize plot
    plt.suptitle(title, fontsize=14, fontweight='bold')
    plt.title(subtitle, fontsize=12, fontweight='normal', style='italic')
    plt.ylabel('Change in Absolute Percentage Points of Convergence', fontsize=12)
    plt.xlabel('Model', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add more detail to y-axis
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0%}'.replace('%', ' pp')))
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_filename)
    print(f"Graph saved as {output_filename}")
    plt.close()

def main():
    # Find all stats_overview.json files
    json_files = glob.glob('results/*/*/stats_overview.json')
    
    results = {}
    
    for json_file in json_files:
        try:
            # Extract model name from path
            model_name = extract_model_name(json_file)
            
            # Load the JSON data
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Initialize model entry
            if model_name not in results:
                results[model_name] = {
                    "absolute_metrics": {},
                    "difference_metrics": {}
                }
            
            # Extract the top_prop_include_invalid from absolute_metrics
            if 'absolute_metrics' in data and 'top_prop_include_invalid' in data['absolute_metrics']:
                results[model_name]["absolute_metrics"] = data['absolute_metrics']['top_prop_include_invalid']
            
            # Extract the top_prop_include_invalid from difference_metrics
            if 'difference_metrics' in data and 'top_prop_include_invalid' in data['difference_metrics']:
                results[model_name]["difference_metrics"] = data['difference_metrics']['top_prop_include_invalid']
                
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
    
    # Write results to a new JSON file
    output_file = 'model_metrics.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Extracted metrics saved to {output_file}")
    
    # Create graphs for the two metrics
    create_difference_metric_graph(results, "coordinate_suppress_cot_vs_control", "suppress_vs_control_diff.png", is_elicit=False)
    create_difference_metric_graph(results, "coordinate_elicit_cot_vs_control", "elicit_vs_control_diff.png", is_elicit=True)

if __name__ == "__main__":
    main()