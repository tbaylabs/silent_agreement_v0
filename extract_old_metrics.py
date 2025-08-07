import json
import os
from pathlib import Path

def extract_metrics_from_stats(file_path):
    """Extract control and elicit CoT metrics from stats_overview.json"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    metrics = {}
    
    # Check if we have the expected structure
    if 'absolute_metrics' in data and 'top_prop_include_invalid' in data['absolute_metrics']:
        abs_metrics = data['absolute_metrics']['top_prop_include_invalid']
        
        # Extract control metrics
        if 'control' in abs_metrics and 'all' in abs_metrics['control']:
            metrics['control_mean'] = abs_metrics['control']['all'].get('mean', None)
        
        # Extract elicit_cot metrics
        if 'coordinate_elicit_cot' in abs_metrics and 'all' in abs_metrics['coordinate_elicit_cot']:
            metrics['elicit_cot_mean'] = abs_metrics['coordinate_elicit_cot']['all'].get('mean', None)
    
    # Also check top_prop_exclude_invalid
    if 'absolute_metrics' in data and 'top_prop_exclude_invalid' in data['absolute_metrics']:
        abs_metrics_ex = data['absolute_metrics']['top_prop_exclude_invalid']
        
        # Extract control metrics (excluding invalid)
        if 'control' in abs_metrics_ex and 'all' in abs_metrics_ex['control']:
            metrics['control_mean_exclude'] = abs_metrics_ex['control']['all'].get('mean', None)
        
        # Extract elicit_cot metrics (excluding invalid)
        if 'coordinate_elicit_cot' in abs_metrics_ex and 'all' in abs_metrics_ex['coordinate_elicit_cot']:
            metrics['elicit_cot_mean_exclude'] = abs_metrics_ex['coordinate_elicit_cot']['all'].get('mean', None)
    
    return metrics

def calculate_differences(metrics):
    """Calculate absolute and proportional differences"""
    results = {}
    
    # Including invalid cases
    if metrics.get('control_mean') is not None and metrics.get('elicit_cot_mean') is not None:
        control_inc = metrics['control_mean']
        elicit_inc = metrics['elicit_cot_mean']
        results['absolute_diff_include'] = abs(elicit_inc - control_inc)
        results['proportional_diff_include'] = abs(elicit_inc - control_inc) / control_inc if control_inc != 0 else None
        results['control_mean_include'] = control_inc
        results['elicit_cot_mean_include'] = elicit_inc
    
    # Excluding invalid cases
    if metrics.get('control_mean_exclude') is not None and metrics.get('elicit_cot_mean_exclude') is not None:
        control_ex = metrics['control_mean_exclude']
        elicit_ex = metrics['elicit_cot_mean_exclude']
        results['absolute_diff_exclude'] = abs(elicit_ex - control_ex)
        results['proportional_diff_exclude'] = abs(elicit_ex - control_ex) / control_ex if control_ex != 0 else None
        results['control_mean_exclude'] = control_ex
        results['elicit_cot_mean_exclude'] = elicit_ex
    
    return results

def main():
    base_path = Path("/Users/graemeford/TBayLabs/silent_agreement/silent_agreement_v1/old_results")
    
    models = {
        "Claude 3.5 Sonnet": base_path / "anthropic/claude-3-5-sonnet-20241022/20250222_140448/stats_overview.json",
        "Claude 3.7 Sonnet": base_path / "anthropic/claude-3-7-sonnet-20250219/20250331_143721/stats_overview.json",
        "Claude Haiku": base_path / "anthropic/20250331_180139/stats_overview.json",
        "GPT-4o": base_path / "openai/gpt-4o/20250523_182505/stats_overview.json",
        "GPT-4o Mini": base_path / "openai/gpt-4o-mini-2024-07-18/20250331_170927/stats_overview.json"
    }
    
    results = {}
    
    for model_name, file_path in models.items():
        if file_path.exists():
            metrics = extract_metrics_from_stats(file_path)
            differences = calculate_differences(metrics)
            results[model_name] = differences
        else:
            print(f"Warning: File not found for {model_name}: {file_path}")
    
    # Generate markdown output
    markdown = "# Model Performance Metrics: Control vs Elicit CoT\n\n"
    markdown += "## Summary Table\n\n"
    
    # Including invalid responses
    markdown += "### Including Invalid Responses\n\n"
    markdown += "| Model | Control Mean | Elicit CoT Mean | Absolute Diff | Proportional Diff |\n"
    markdown += "|-------|-------------|-----------------|---------------|-------------------|\n"
    
    for model_name, data in results.items():
        if 'control_mean_include' in data:
            control = data.get('control_mean_include', 0)
            elicit = data.get('elicit_cot_mean_include', 0)
            abs_diff = data.get('absolute_diff_include', 0)
            prop_diff = data.get('proportional_diff_include', 0)
            
            markdown += f"| {model_name} | {control:.3f} | {elicit:.3f} | {abs_diff:.3f} | {prop_diff:.1%} |\n"
    
    # Excluding invalid responses
    markdown += "\n### Excluding Invalid Responses\n\n"
    markdown += "| Model | Control Mean | Elicit CoT Mean | Absolute Diff | Proportional Diff |\n"
    markdown += "|-------|-------------|-----------------|---------------|-------------------|\n"
    
    for model_name, data in results.items():
        if 'control_mean_exclude' in data:
            control = data.get('control_mean_exclude', 0)
            elicit = data.get('elicit_cot_mean_exclude', 0)
            abs_diff = data.get('absolute_diff_exclude', 0)
            prop_diff = data.get('proportional_diff_exclude', 0)
            
            markdown += f"| {model_name} | {control:.3f} | {elicit:.3f} | {abs_diff:.3f} | {prop_diff:.1%} |\n"
    
    # Detailed breakdown
    markdown += "\n## Detailed Breakdown by Model\n\n"
    
    for model_name, data in results.items():
        markdown += f"### {model_name}\n\n"
        
        if 'control_mean_include' in data:
            markdown += "**Including Invalid Responses:**\n"
            markdown += f"- Control Mean: {data['control_mean_include']:.3f}\n"
            markdown += f"- Elicit CoT Mean: {data['elicit_cot_mean_include']:.3f}\n"
            markdown += f"- Absolute Difference: {data['absolute_diff_include']:.3f}\n"
            markdown += f"- Proportional Difference: {data['proportional_diff_include']:.1%}\n\n"
        
        if 'control_mean_exclude' in data:
            markdown += "**Excluding Invalid Responses:**\n"
            markdown += f"- Control Mean: {data['control_mean_exclude']:.3f}\n"
            markdown += f"- Elicit CoT Mean: {data['elicit_cot_mean_exclude']:.3f}\n"
            markdown += f"- Absolute Difference: {data['absolute_diff_exclude']:.3f}\n"
            markdown += f"- Proportional Difference: {data['proportional_diff_exclude']:.1%}\n\n"
    
    # Save results
    with open('old_metrics_summary.md', 'w') as f:
        f.write(markdown)
    
    with open('old_metrics_data.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Metrics extracted and saved to old_metrics_summary.md and old_metrics_data.json")
    print("\n" + markdown)

if __name__ == "__main__":
    main()