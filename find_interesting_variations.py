import json
from pathlib import Path

def find_interesting_variations():
    with open("control_emoji_distributions.json", 'r') as f:
        data = json.load(f)
    
    interesting_cases = []
    
    option_sets = set()
    for model_data in data.values():
        option_sets.update(model_data.keys())
    
    for option_set in option_sets:
        model_behaviors = {}
        
        for model_name, model_data in data.items():
            if option_set in model_data:
                set_data = model_data[option_set]
                model_behaviors[model_name] = {
                    "top_response": set_data["top_response"],
                    "top_proportion": set_data["top_proportion"],
                    "proportions": set_data["response_proportions"],
                    "options": set_data["options_list"]
                }
        
        if len(model_behaviors) == 3:
            models = list(model_behaviors.keys())
            top_responses = [model_behaviors[m]["top_response"] for m in models]
            top_props = [model_behaviors[m]["top_proportion"] for m in models]
            
            # Case 1: All models converge strongly (>80%) but on different options
            if all(p >= 0.8 for p in top_props if p is not None):
                unique_responses = set(top_responses)
                if len(unique_responses) > 1:
                    interesting_cases.append({
                        "type": "HIGH_CONVERGENCE_DIFFERENT_OPTIONS",
                        "option_set": option_set,
                        "description": f"All models converge strongly (≥80%) but on {len(unique_responses)} different options",
                        "models": model_behaviors
                    })
            
            # Case 2: Models choose completely different options with moderate to high confidence
            elif len(set(top_responses)) == 3 and all(p >= 0.5 for p in top_props if p is not None):
                interesting_cases.append({
                    "type": "THREE_WAY_SPLIT",
                    "option_set": option_set,
                    "description": "Each model chooses a different option with ≥50% confidence",
                    "models": model_behaviors
                })
            
            # Case 3: One model behaves very differently from the others
            if len(set(top_responses)) == 2:
                response_counts = {r: top_responses.count(r) for r in set(top_responses)}
                minority_response = min(response_counts, key=response_counts.get)
                majority_response = max(response_counts, key=response_counts.get)
                
                minority_model = [models[i] for i, r in enumerate(top_responses) if r == minority_response][0]
                majority_models = [models[i] for i, r in enumerate(top_responses) if r == majority_response]
                
                minority_prop = model_behaviors[minority_model]["top_proportion"]
                majority_props = [model_behaviors[m]["top_proportion"] for m in majority_models]
                
                if minority_prop >= 0.7 and all(p >= 0.7 for p in majority_props):
                    interesting_cases.append({
                        "type": "ONE_MODEL_DIFFERENT",
                        "option_set": option_set,
                        "description": f"{minority_model.split('-')[2]} chooses {minority_response} while the other two choose {majority_response}",
                        "minority_model": minority_model,
                        "minority_choice": minority_response,
                        "minority_proportion": minority_prop,
                        "majority_choice": majority_response,
                        "models": model_behaviors
                    })
            
            # Case 4: Large variance in confidence levels for the same choice
            if len(set(top_responses)) == 1:
                prop_variance = max(top_props) - min(top_props)
                if prop_variance >= 0.4:
                    interesting_cases.append({
                        "type": "SAME_CHOICE_DIFFERENT_CONFIDENCE",
                        "option_set": option_set,
                        "description": f"All choose {top_responses[0]} but with confidence ranging from {min(top_props):.1%} to {max(top_props):.1%}",
                        "choice": top_responses[0],
                        "confidence_range": [min(top_props), max(top_props)],
                        "models": model_behaviors
                    })
    
    return interesting_cases

if __name__ == "__main__":
    interesting = find_interesting_variations()
    
    # Save full analysis
    with open("interesting_variations.json", 'w') as f:
        json.dump(interesting, f, indent=2, ensure_ascii=False)
    
    print(f"Found {len(interesting)} interesting cases\n")
    
    # Print summary by type
    types_count = {}
    for case in interesting:
        case_type = case["type"]
        types_count[case_type] = types_count.get(case_type, 0) + 1
    
    print("Summary by type:")
    for case_type, count in sorted(types_count.items()):
        print(f"  {case_type}: {count} cases")
    
    # Print most interesting examples
    print("\n" + "="*80)
    print("MOST INTERESTING EXAMPLES:")
    print("="*80)
    
    # Show examples of each type
    shown_types = set()
    for case in interesting:
        if case["type"] not in shown_types and len(shown_types) < 5:
            shown_types.add(case["type"])
            print(f"\n[{case['type']}]")
            print(f"Option Set: {case['option_set']}")
            print(f"Description: {case['description']}")
            
            if "models" in case:
                print("\nModel behaviors:")
                for model, behavior in case["models"].items():
                    model_short = model.split('-')[2]  # Get just the model size (4.1, mini, nano)
                    print(f"  {model_short:4s}: {behavior['top_response']} ({behavior['top_proportion']:.1%})")
                    
                    # Show full distribution for this example
                    if case["type"] in ["HIGH_CONVERGENCE_DIFFERENT_OPTIONS", "THREE_WAY_SPLIT"]:
                        sorted_props = sorted(behavior["proportions"].items(), key=lambda x: x[1], reverse=True)
                        dist_str = ", ".join([f"{k}:{v:.1%}" for k, v in sorted_props[:3] if v > 0])
                        print(f"        Distribution: {dist_str}")
            print("-"*80)