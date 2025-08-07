import json
from pathlib import Path

def extract_metrics(file_path):
    """Extract control and elicit CoT metrics from stats_overview.json"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    results = {}
    
    # Extract from absolute_metrics
    if 'absolute_metrics' in data:
        # Including invalid
        if 'top_prop_include_invalid' in data['absolute_metrics']:
            inc = data['absolute_metrics']['top_prop_include_invalid']
            if 'all' in inc:
                all_inc = inc['all']
                if 'control_suppress_cot_stats' in all_inc:
                    # Control is in the control_suppress_cot_stats
                    results['control_include'] = all_inc['control_suppress_cot_stats'].get('mean', None)
                if 'coordinate_elicit_cot_stats' in all_inc:
                    results['elicit_cot_include'] = all_inc['coordinate_elicit_cot_stats'].get('mean', None)
        
        # Excluding invalid
        if 'top_prop_exclude_invalid' in data['absolute_metrics']:
            exc = data['absolute_metrics']['top_prop_exclude_invalid']
            if 'all' in exc:
                all_exc = exc['all']
                if 'control_suppress_cot_stats' in all_exc:
                    results['control_exclude'] = all_exc['control_suppress_cot_stats'].get('mean', None)
                if 'coordinate_elicit_cot_stats' in all_exc:
                    results['elicit_cot_exclude'] = all_exc['coordinate_elicit_cot_stats'].get('mean', None)
    
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
    
    markdown = "# Model Performance Metrics: Control vs Elicit CoT\n\n"
    markdown += "## Summary Table\n\n"
    
    # Including invalid responses
    markdown += "### Including Invalid Responses\n\n"
    markdown += "| Model | Control Mean | Elicit CoT Mean | Absolute Diff | Proportional Diff |\n"
    markdown += "|-------|-------------|-----------------|---------------|-------------------|\n"
    
    all_results = {}
    
    for model_name, file_path in models.items():
        if file_path.exists():
            metrics = extract_metrics(file_path)
            all_results[model_name] = metrics
            
            if metrics.get('control_include') is not None and metrics.get('elicit_cot_include') is not None:
                control = metrics['control_include']
                elicit = metrics['elicit_cot_include']
                abs_diff = abs(elicit - control)
                prop_diff = abs_diff / control if control != 0 else 0
                
                markdown += f"| {model_name} | {control:.3f} | {elicit:.3f} | {abs_diff:.3f} | {prop_diff:.1%} |\n"
    
    # Excluding invalid responses
    markdown += "\n### Excluding Invalid Responses\n\n"
    markdown += "| Model | Control Mean | Elicit CoT Mean | Absolute Diff | Proportional Diff |\n"
    markdown += "|-------|-------------|-----------------|---------------|-------------------|\n"
    
    for model_name in models.keys():
        if model_name in all_results:
            metrics = all_results[model_name]
            
            if metrics.get('control_exclude') is not None and metrics.get('elicit_cot_exclude') is not None:
                control = metrics['control_exclude']
                elicit = metrics['elicit_cot_exclude']
                abs_diff = abs(elicit - control)
                prop_diff = abs_diff / control if control != 0 else 0
                
                markdown += f"| {model_name} | {control:.3f} | {elicit:.3f} | {abs_diff:.3f} | {prop_diff:.1%} |\n"
    
    # Detailed breakdown
    markdown += "\n## Detailed Breakdown by Model\n\n"
    
    for model_name in models.keys():
        if model_name in all_results:
            metrics = all_results[model_name]
            markdown += f"### {model_name}\n\n"
            
            if metrics.get('control_include') is not None and metrics.get('elicit_cot_include') is not None:
                control = metrics['control_include']
                elicit = metrics['elicit_cot_include']
                abs_diff = abs(elicit - control)
                prop_diff = abs_diff / control if control != 0 else 0
                
                markdown += "**Including Invalid Responses:**\n"
                markdown += f"- Control Mean: {control:.3f}\n"
                markdown += f"- Elicit CoT Mean: {elicit:.3f}\n"
                markdown += f"- Absolute Difference: {abs_diff:.3f}\n"
                markdown += f"- Proportional Difference: {prop_diff:.1%}\n\n"
            
            if metrics.get('control_exclude') is not None and metrics.get('elicit_cot_exclude') is not None:
                control = metrics['control_exclude']
                elicit = metrics['elicit_cot_exclude']
                abs_diff = abs(elicit - control)
                prop_diff = abs_diff / control if control != 0 else 0
                
                markdown += "**Excluding Invalid Responses:**\n"
                markdown += f"- Control Mean: {control:.3f}\n"
                markdown += f"- Elicit CoT Mean: {elicit:.3f}\n"
                markdown += f"- Absolute Difference: {abs_diff:.3f}\n"
                markdown += f"- Proportional Difference: {prop_diff:.1%}\n\n"
    
    # Notes
    markdown += "## Notes\n\n"
    markdown += "- **Control Mean**: The mean proportion of responses that converge on the most common option in the control condition\n"
    markdown += "- **Elicit CoT Mean**: The mean proportion when Chain-of-Thought reasoning is explicitly elicited\n"
    markdown += "- **Absolute Difference**: The absolute percentage point difference between Elicit CoT and Control\n"
    markdown += "- **Proportional Difference**: The relative change as a proportion of the Control mean\n"
    
    print(markdown)
    
    # Save to file
    with open('model_metrics_summary.md', 'w') as f:
        f.write(markdown)
    
    print("\nSaved to model_metrics_summary.md")

if __name__ == "__main__":
    main()