#!/usr/bin/env python3
"""
Analyze patterns in options performance across models.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

def load_performance_data():
    """Load the CSV data and return as a dictionary."""
    csv_path = Path("/Users/graemeford/TBayLabs/silent_agreement/silent_agreement_v1/data/results/options_performance_comparison.csv")
    
    data = {}
    models = []
    
    with open(csv_path, 'r') as f:
        header = f.readline().strip().split(',')
        models = header[1:]  # Skip 'Option' column
        
        for line in f:
            parts = line.strip().split(',')
            option = parts[0]
            scores = [float(x) for x in parts[1:]]
            data[option] = dict(zip(models, scores))
    
    return data, models

def analyze_patterns():
    data, models = load_performance_data()
    
    # Model order: standard (most powerful), mini, nano (least powerful)
    print("=== OPTIONS PERFORMANCE ANALYSIS ===\n")
    
    # 1. Overall averages
    print("1. Model Performance Summary:")
    print("-" * 40)
    for model in models:
        scores = [data[opt][model] for opt in data]
        avg = sum(scores) / len(scores)
        print(f"{model}: {avg:.3f}")
    
    # 2. Options above different thresholds
    print("\n2. Options Performance Distribution:")
    print("-" * 40)
    
    thresholds = [0.9, 0.8, 0.7, 0.5]
    for threshold in thresholds:
        print(f"\nOptions ≥ {threshold}:")
        for model in models:
            count = sum(1 for opt in data if data[opt][model] >= threshold)
            pct = count / len(data) * 100
            print(f"  {model}: {count}/80 ({pct:.1f}%)")
    
    # 3. Options close to 90% (between 0.85 and 0.95)
    print("\n3. Options Close to 90% (0.85-0.95):")
    print("-" * 40)
    close_to_90 = defaultdict(list)
    
    for option in data:
        for model in models:
            score = data[option][model]
            if 0.85 <= score <= 0.95:
                close_to_90[model].append((option, score))
    
    for model in models:
        print(f"\n{model}:")
        items = sorted(close_to_90[model], key=lambda x: x[1], reverse=True)
        for opt, score in items[:10]:  # Top 10
            print(f"  {opt}: {score:.3f}")
    
    # 4. Options at ceiling (≥ 0.95)
    print("\n4. Options at Ceiling (≥ 0.95):")
    print("-" * 40)
    
    ceiling_options = defaultdict(list)
    for option in data:
        for model in models:
            score = data[option][model]
            if score >= 0.95:
                ceiling_options[model].append((option, score))
    
    for model in models:
        print(f"\n{model}: {len(ceiling_options[model])} options")
        for opt, score in sorted(ceiling_options[model], key=lambda x: x[1], reverse=True):
            print(f"  {opt}: {score:.3f}")
    
    # 5. Analyze patterns by option type
    print("\n5. Performance by Option Type:")
    print("-" * 40)
    
    type_scores = defaultdict(lambda: defaultdict(list))
    category_scores = defaultdict(lambda: defaultdict(list))
    
    for option in data:
        parts = option.split('|')
        if len(parts) == 3:
            name, category, opt_type = parts
            for model in models:
                type_scores[opt_type][model].append(data[option][model])
                category_scores[category][model].append(data[option][model])
    
    print("\nBy Type (symbol vs text):")
    for opt_type in sorted(type_scores.keys()):
        print(f"\n{opt_type}:")
        for model in models:
            scores = type_scores[opt_type][model]
            avg = sum(scores) / len(scores)
            print(f"  {model}: {avg:.3f}")
    
    print("\nBy Category (set vs disparate):")
    for category in sorted(category_scores.keys()):
        print(f"\n{category}:")
        for model in models:
            scores = category_scores[category][model]
            avg = sum(scores) / len(scores)
            print(f"  {model}: {avg:.3f}")
    
    # 6. Options with unexpected patterns (nano > standard)
    print("\n6. Unexpected Patterns (weaker model > stronger model):")
    print("-" * 40)
    
    standard = models[0]  # gpt-4.1-2025-04-14
    mini = models[1]      # gpt-4.1-mini-2025-04-14
    nano = models[2]      # gpt-4.1-nano-2025-04-14
    
    print("\nNano > Standard:")
    unexpected_nano = [(opt, data[opt][nano], data[opt][standard]) 
                      for opt in data if data[opt][nano] > data[opt][standard] + 0.1]
    
    for opt, nano_score, standard_score in sorted(unexpected_nano, key=lambda x: x[1]-x[2], reverse=True)[:10]:
        diff = nano_score - standard_score
        print(f"  {opt}: nano={nano_score:.3f}, standard={standard_score:.3f} (diff={diff:.3f})")
    
    # 7. Options with large variance across models
    print("\n7. Options with High Variance Across Models:")
    print("-" * 40)
    
    variances = []
    for option in data:
        scores = [data[option][model] for model in models]
        variance = max(scores) - min(scores)
        variances.append((option, variance, scores))
    
    variances.sort(key=lambda x: x[1], reverse=True)
    
    for opt, var, scores in variances[:10]:
        scores_str = ", ".join(f"{s:.3f}" for s in scores)
        print(f"  {opt}: variance={var:.3f} [{scores_str}]")
    
    # 8. Recommendations
    print("\n8. Recommendations for Ceiling Effects:")
    print("-" * 40)
    
    problematic = []
    for option in data:
        # Check if any model has > 0.9
        max_score = max(data[option][model] for model in models)
        if max_score > 0.9:
            problematic.append((option, max_score))
    
    print(f"\nTotal options with potential ceiling effects (>0.9 in any model): {len(problematic)}")
    print("\nMost problematic options:")
    for opt, score in sorted(problematic, key=lambda x: x[1], reverse=True)[:15]:
        print(f"  {opt}: {score:.3f}")

if __name__ == "__main__":
    analyze_patterns()