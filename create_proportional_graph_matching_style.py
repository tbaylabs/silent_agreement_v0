import json
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

def extract_metrics_with_stats(file_path):
    """Extract metrics including standard deviations for error bars"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    results = {}
    
    # Get difference metrics for proportional calculation
    if 'difference_metrics' in data and 'top_prop_exclude_invalid' in data['difference_metrics']:
        diff = data['difference_metrics']['top_prop_exclude_invalid']
        if 'all' in diff and 'coordinate_elicit_cot_vs_control' in diff['all']:
            elicit_diff = diff['all']['coordinate_elicit_cot_vs_control']
            results['diff_mean'] = elicit_diff.get('mean', 0)
            results['diff_sd'] = elicit_diff.get('sd', 0)
    
    # Get absolute metrics for base values
    if 'absolute_metrics' in data:
        if 'top_prop_exclude_invalid' in data['absolute_metrics']:
            exc = data['absolute_metrics']['top_prop_exclude_invalid']
            if 'all' in exc:
                all_exc = exc['all']
                if 'control_suppress_cot_stats' in all_exc:
                    results['control'] = all_exc['control_suppress_cot_stats'].get('mean', None)
                if 'coordinate_elicit_cot_stats' in all_exc:
                    results['elicit'] = all_exc['coordinate_elicit_cot_stats'].get('mean', None)
    
    return results

def calculate_proportional_error(control_mean, diff_mean, diff_sd):
    """Calculate proportional change and approximate error bars"""
    if control_mean == 0:
        return 0, 0
    
    # Proportional change
    prop_change = diff_mean / control_mean
    
    # Approximate proportional SD (using delta method)
    # For ratio, relative error ≈ sqrt((sd_diff/diff)^2)
    # But we'll scale it proportionally to control
    prop_sd = diff_sd / control_mean
    
    return prop_change, prop_sd

def create_matching_style_graph():
    base_path = Path("/Users/graemeford/TBayLabs/silent_agreement/silent_agreement_v1")
    
    models = {
        "claude-3-5-haiku-20241022": base_path / "old_results/anthropic/20250331_180139/stats_overview.json",
        "gpt-4o-mini-2024-07-18": base_path / "old_results/openai/gpt-4o-mini-2024-07-18/20250331_170927/stats_overview.json",
        "llama-3.3-70b-versatile": base_path / "old_results/groq/llama-3.3-70b-versatile/20250222_125306/stats_overview.json",  # Updated to correct eval
        "claude-3-5-sonnet-20241022": base_path / "old_results/anthropic/claude-3-5-sonnet-20241022/20250222_140448/stats_overview.json",
        "chatgpt-4o-latest": base_path / "old_results/openai/20250331_161238/stats_overview.json",
        "claude-3-7-sonnet-20250219": base_path / "old_results/anthropic/claude-3-7-sonnet-20250219/20250331_143721/stats_overview.json"
    }
    
    # Collect data
    model_data = []
    
    for model_name, file_path in models.items():
        if file_path.exists():
            metrics = extract_metrics_with_stats(file_path)
            
            if metrics.get('control') and metrics.get('diff_mean') is not None:
                prop_change, prop_sd = calculate_proportional_error(
                    metrics['control'], 
                    metrics['diff_mean'],
                    metrics.get('diff_sd', 0)
                )
                
                # Calculate error bars (using 1.96 for 95% CI)
                error_lower = 1.96 * prop_sd
                error_upper = 1.96 * prop_sd
                
                model_data.append({
                    'model': model_name,
                    'prop_change': prop_change,
                    'error_lower': error_lower,
                    'error_upper': error_upper
                })
    
    # Sort by proportional change
    model_data.sort(key=lambda x: x['prop_change'])
    
    # Prepare data for plotting
    models = [item['model'] for item in model_data]
    prop_changes = [item['prop_change'] for item in model_data]
    errors = [[item['error_lower'] for item in model_data],
              [item['error_upper'] for item in model_data]]
    
    # Create the plot matching the original style more closely
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Use a more subdued blue color similar to the original
    # The original appears to be a sky blue or steel blue
    marker_color = '#5B9BD5'  # A more subdued, professional blue
    
    # Plot error bars with points
    x_pos = np.arange(len(models))
    ax.errorbar(x_pos, prop_changes, yerr=errors, 
                fmt='o', markersize=8, color=marker_color,
                ecolor='black', elinewidth=1.5, capsize=5, capthick=1.5)
    
    # Add horizontal line at y=0 with more subtle red
    ax.axhline(y=0, color='#D9534F', linestyle='--', linewidth=1, alpha=0.5)
    
    # Add horizontal grid matching original style
    ax.yaxis.grid(True, linestyle='--', alpha=0.3, color='gray')
    ax.set_axisbelow(True)
    
    # Set labels and title - matching original formatting
    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel('Change in Absolute Percentage Points of Convergence', fontsize=11)
    
    # Title with same formatting as original
    title = 'Change in Performance: Coordination with Elicited Chain-of-Thought vs Control'
    subtitle = '(Positive values indicate improved convergence on top response)'
    ax.set_title(f'{title}\n{subtitle}', fontsize=12, pad=20)
    
    # Format y-axis as percentage points (matching original)
    y_ticks = ax.get_yticks()
    # Convert proportional to percentage points
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f'{int(y*100)} pp' for y in y_ticks])
    
    # Set x-axis labels
    ax.set_xticks(x_pos)
    ax.set_xticklabels(models, rotation=45, ha='right')
    
    # Match the original's clean style
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the plot
    output_file = 'elicit_vs_control_proportional_diff_matching.png'
    plt.savefig(output_file, dpi=100, bbox_inches='tight', facecolor='white')
    print(f"Graph saved as {output_file}")
    plt.close()
    
    # Also create version with percentage labels
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plot error bars with points using subdued blue
    ax.errorbar(x_pos, prop_changes, yerr=errors, 
                fmt='o', markersize=8, color=marker_color,
                ecolor='black', elinewidth=1.5, capsize=5, capthick=1.5)
    
    # Add horizontal line at y=0
    ax.axhline(y=0, color='#D9534F', linestyle='--', linewidth=1, alpha=0.5)
    
    # Add horizontal grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.3, color='gray')
    ax.set_axisbelow(True)
    
    # Set labels and title - for proportional version
    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel('Proportional Change in Convergence', fontsize=11)
    title = 'Proportional Change in Performance: Coordination with Elicited Chain-of-Thought vs Control'
    subtitle = '(Positive values indicate improved convergence on top response)'
    ax.set_title(f'{title}\n{subtitle}', fontsize=12, pad=20)
    
    # Format y-axis as percentage
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f'{int(y*100)}%' for y in y_ticks])
    
    # Set x-axis labels
    ax.set_xticks(x_pos)
    ax.set_xticklabels(models, rotation=45, ha='right')
    
    # Match original's clean style
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the plot with proportional labels
    output_file2 = 'elicit_vs_control_proportional_pct.png'
    plt.savefig(output_file2, dpi=100, bbox_inches='tight', facecolor='white')
    print(f"Alternative version with percentage labels saved as {output_file2}")
    
    # Print the actual values for verification
    print("\nModel performance (sorted by proportional change):")
    for item in model_data:
        print(f"  {item['model']}: {item['prop_change']*100:.1f}%")

if __name__ == "__main__":
    create_matching_style_graph()