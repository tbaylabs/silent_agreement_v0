import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats

def load_group_results(file_path):
    """Load group results JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def calculate_top_proportion(response_dist):
    """Calculate the proportion of the most common response"""
    # Remove invalid responses from consideration
    valid_responses = {k: v for k, v in response_dist.items() 
                      if k not in ['invalid', 'fail_subset_invalid']}
    
    if not valid_responses:
        return 0
    
    total = sum(valid_responses.values())
    if total == 0:
        return 0
    
    max_count = max(valid_responses.values())
    return max_count / total

def get_paired_proportions(group_data):
    """Extract paired proportions for control and suppress_cot conditions"""
    
    # Get unique option sets
    option_sets = set()
    for key, value in group_data.items():
        option_sets.add(value['option_id'])
    
    paired_data = []
    
    for option_id in sorted(option_sets):
        # Find control and suppress_cot data for this option set
        control_key = f"control_suppress_cot-{option_id}"
        suppress_key = f"coordinate_suppress_cot-{option_id}"
        
        if control_key in group_data and suppress_key in group_data:
            control_prop = calculate_top_proportion(group_data[control_key]['response_distribution'])
            suppress_prop = calculate_top_proportion(group_data[suppress_key]['response_distribution'])
            
            paired_data.append({
                'option_id': option_id,
                'control': control_prop,
                'suppress': suppress_prop,
                'absolute_diff': suppress_prop - control_prop,
                'proportional_diff': (suppress_prop - control_prop) / control_prop if control_prop > 0 else 0
            })
    
    return paired_data

def calculate_paired_statistics(paired_data):
    """Calculate mean, SD, and confidence intervals for paired differences"""
    
    # Extract absolute and proportional differences
    abs_diffs = [d['absolute_diff'] for d in paired_data]
    prop_diffs = [d['proportional_diff'] for d in paired_data]
    
    n = len(paired_data)
    df = n - 1  # degrees of freedom
    
    # Calculate statistics for absolute differences
    abs_mean = np.mean(abs_diffs)
    abs_sd = np.std(abs_diffs, ddof=1)  # Sample SD with Bessel's correction
    abs_se = abs_sd / np.sqrt(n)
    
    # Calculate statistics for proportional differences
    prop_mean = np.mean(prop_diffs)
    prop_sd = np.std(prop_diffs, ddof=1)
    prop_se = prop_sd / np.sqrt(n)
    
    # t-critical value for 90% two-sided CI with df=19
    t_critical = stats.t.ppf(0.95, df)  # About 1.729 for df=19
    
    return {
        'n': n,
        'df': df,
        't_critical': t_critical,
        'absolute': {
            'mean': abs_mean,
            'sd': abs_sd,
            'se': abs_se,
            'ci_lower': abs_mean - t_critical * abs_se,
            'ci_upper': abs_mean + t_critical * abs_se,
            'ci_width': t_critical * abs_se
        },
        'proportional': {
            'mean': prop_mean,
            'sd': prop_sd,
            'se': prop_se,
            'ci_lower': prop_mean - t_critical * prop_se,
            'ci_upper': prop_mean + t_critical * prop_se,
            'ci_width': t_critical * prop_se
        },
        'paired_data': paired_data
    }

def process_all_models():
    """Process all models and calculate their statistics"""
    
    base_path = Path("/Users/graemeford/TBayLabs/silent_agreement/silent_agreement_v1")
    
    models = {
        "claude-3-5-haiku-20241022": base_path / "old_results/anthropic/20250331_180139/group_results.json",
        "gpt-4o-mini-2024-07-18": base_path / "old_results/openai/gpt-4o-mini-2024-07-18/20250331_170927/group_results.json",
        "llama-3.3-70b-versatile": base_path / "old_results/groq/llama-3.3-70b-versatile/20250222_125306/group_results.json",
        "claude-3-5-sonnet-20241022": base_path / "old_results/anthropic/claude-3-5-sonnet-20241022/20250222_140448/group_results.json",
        "chatgpt-4o-latest": base_path / "old_results/openai/20250331_161238/group_results.json",
        "claude-3-7-sonnet-20250219": base_path / "old_results/anthropic/claude-3-7-sonnet-20250219/20250331_143721/group_results.json"
    }
    
    results = {}
    
    for model_name, file_path in models.items():
        if file_path.exists():
            group_data = load_group_results(file_path)
            paired_data = get_paired_proportions(group_data)
            stats = calculate_paired_statistics(paired_data)
            results[model_name] = stats
    
    return results

def create_suppress_graphs(results):
    """Create both graphs for suppress CoT vs control"""
    
    # Prepare data for plotting
    model_data_abs = []
    model_data_prop = []
    
    for model_name, stats in results.items():
        # Absolute data (convert to percentage points)
        model_data_abs.append({
            'model': model_name,
            'mean': stats['absolute']['mean'] * 100,  # Convert to percentage points
            'ci_width': stats['absolute']['ci_width'] * 100
        })
        
        # Proportional data (convert to percentage)
        model_data_prop.append({
            'model': model_name,
            'mean': stats['proportional']['mean'] * 100,  # Convert to percentage
            'ci_width': stats['proportional']['ci_width'] * 100
        })
    
    # Sort both by mean
    model_data_abs.sort(key=lambda x: x['mean'])
    model_data_prop.sort(key=lambda x: x['mean'])
    
    # Common settings
    marker_color = '#5B9BD5'
    fig_size = (14, 8)
    y_min = -30
    y_max = 80
    y_ticks = np.arange(y_min, y_max + 10, 10)
    
    # =================
    # ABSOLUTE METRIC GRAPH (SUPPRESS)
    # =================
    fig, ax = plt.subplots(figsize=fig_size)
    
    # Extract data for plotting
    models = [d['model'] for d in model_data_abs]
    means = [d['mean'] for d in model_data_abs]
    errors = [d['ci_width'] for d in model_data_abs]
    
    # Plot error bars
    x_pos = np.arange(len(models))
    ax.errorbar(x_pos, means, yerr=errors,
                fmt='o', markersize=8, color=marker_color,
                ecolor='black', elinewidth=1.5, capsize=5, capthick=1.5)
    
    # Add horizontal line at y=0
    ax.axhline(y=0, color='#D9534F', linestyle='--', linewidth=1, alpha=0.5)
    
    # Add grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.3, color='gray')
    ax.set_axisbelow(True)
    
    # Labels and title
    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel('Absolute Change in Convergence (percentage points)', fontsize=11)
    title = 'Change in Performance: Out-of-context coordination vs Control'
    subtitle = '(Absolute percentage point change in convergence on top response)'
    ax.set_title(f'{title}\n{subtitle}', fontsize=12, pad=20)
    
    # Set y-axis
    ax.set_ylim(y_min, y_max)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f'{int(y)} pp' for y in y_ticks])
    
    # Set x-axis labels
    ax.set_xticks(x_pos)
    ax.set_xticklabels(models, rotation=45, ha='right')
    
    # Clean style
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('suppress_absolute_metric.png', dpi=100, bbox_inches='tight', facecolor='white')
    plt.close()
    
    # =================
    # PROPORTIONAL METRIC GRAPH (SUPPRESS)
    # =================
    fig, ax = plt.subplots(figsize=fig_size)
    
    # Extract data for plotting
    models = [d['model'] for d in model_data_prop]
    means = [d['mean'] for d in model_data_prop]
    errors = [d['ci_width'] for d in model_data_prop]
    
    # Plot error bars
    x_pos = np.arange(len(models))
    ax.errorbar(x_pos, means, yerr=errors,
                fmt='o', markersize=8, color=marker_color,
                ecolor='black', elinewidth=1.5, capsize=5, capthick=1.5)
    
    # Add horizontal line at y=0
    ax.axhline(y=0, color='#D9534F', linestyle='--', linewidth=1, alpha=0.5)
    
    # Add grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.3, color='gray')
    ax.set_axisbelow(True)
    
    # Labels and title
    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel('Proportional Change in Convergence (%)', fontsize=11)
    title = 'Proportional Change in Performance: Out-of-context coordination vs Control'
    subtitle = '(Relative percentage change in convergence on top response)'
    ax.set_title(f'{title}\n{subtitle}', fontsize=12, pad=20)
    
    # Set y-axis - same as absolute for easy comparison
    ax.set_ylim(y_min, y_max)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f'{int(y)}%' for y in y_ticks])
    
    # Set x-axis labels
    ax.set_xticks(x_pos)
    ax.set_xticklabels(models, rotation=45, ha='right')
    
    # Clean style
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('suppress_proportional_metric.png', dpi=100, bbox_inches='tight', facecolor='white')
    plt.close()

def main():
    print("Creating SUPPRESS CoT vs CONTROL graphs...")
    print("Using paired t-test methodology with 90% two-sided CI\n")
    
    results = process_all_models()
    
    # Create graphs
    create_suppress_graphs(results)
    
    print("Created graphs:")
    print("  - suppress_absolute_metric.png (y-axis: -30 to 80 pp)")
    print("  - suppress_proportional_metric.png (y-axis: -30 to 80%)")
    print("\nBoth graphs show the effect of suppressing Chain-of-Thought (out-of-context coordination)")
    
    print("\n" + "="*70)
    print("SUMMARY OF SUPPRESS CoT METRICS")
    print("="*70)
    
    # Sort by absolute mean for display
    sorted_models = sorted(results.items(), key=lambda x: x[1]['absolute']['mean'])
    
    print(f"{'Model':<30} {'Absolute (pp)':<20} {'Proportional (%)':<20}")
    print("-" * 70)
    
    for model_name, stats in sorted_models:
        abs_mean = stats['absolute']['mean'] * 100
        abs_ci = stats['absolute']['ci_width'] * 100
        prop_mean = stats['proportional']['mean'] * 100
        prop_ci = stats['proportional']['ci_width'] * 100
        
        abs_str = f"{abs_mean:+6.1f} ± {abs_ci:4.1f}"
        prop_str = f"{prop_mean:+6.1f} ± {prop_ci:4.1f}"
        
        print(f"{model_name:<30} {abs_str:<20} {prop_str:<20}")
    
    print("\nNote: Negative values indicate reduced convergence when CoT is suppressed")
    print("      Positive values indicate increased convergence when CoT is suppressed")

if __name__ == "__main__":
    main()