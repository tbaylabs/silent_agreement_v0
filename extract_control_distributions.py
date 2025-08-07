import json
import os
from pathlib import Path

def extract_control_distributions():
    base_path = Path("/Users/graemeford/TBayLabs/silent_agreement/silent_agreement_v1/data/results/base/openai")
    
    models = {
        "gpt-4.1-2025-04-14": base_path / "gpt-4.1-2025-04-14/20250619_125706/options_results.json",
        "gpt-4.1-mini-2025-04-14": base_path / "gpt-4.1-mini-2025-04-14/20250619_115622/options_results.json",
        "gpt-4.1-nano-2025-04-14": base_path / "gpt-4.1-nano-2025-04-14/20250619_114142/options_results.json"
    }
    
    consolidated_data = {}
    
    for model_name, file_path in models.items():
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        model_control_data = {}
        
        for option_set_key, option_set_data in data.items():
            if "trial_blocks_by_condition" in option_set_data and "control" in option_set_data["trial_blocks_by_condition"]:
                control_data = option_set_data["trial_blocks_by_condition"]["control"]
                
                response_dist = control_data.get("response_distribution", {})
                
                clean_dist = {}
                total_valid = 0
                for key, value in response_dist.items():
                    if not key.endswith("_count") and key not in ["ooc_invalid_count", "illegible_invalid_count"]:
                        clean_dist[key] = value
                        total_valid += value
                
                proportions = {}
                if total_valid > 0:
                    for key, value in clean_dist.items():
                        proportions[key] = round(value / total_valid, 3)
                
                model_control_data[option_set_key] = {
                    "options_list": option_set_data.get("options_list", []),
                    "response_counts": clean_dist,
                    "response_proportions": proportions,
                    "total_responses": total_valid,
                    "top_response": control_data["stats"].get("top_response"),
                    "top_proportion": control_data["stats"].get("top_prop_exclude_invalid")
                }
        
        consolidated_data[model_name] = model_control_data
    
    return consolidated_data

def analyze_variations(data):
    analysis_results = []
    
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
                    "proportions": set_data["response_proportions"]
                }
        
        if len(model_behaviors) == 3:
            top_responses = [b["top_response"] for b in model_behaviors.values()]
            top_props = [b["top_proportion"] for b in model_behaviors.values()]
            
            all_same = len(set(top_responses)) == 1
            all_different = len(set(top_responses)) == 3
            
            high_convergence = all(p >= 0.75 for p in top_props if p is not None)
            
            prop_variance = max(top_props) - min(top_props) if all(p is not None for p in top_props) else 0
            
            if all_different and high_convergence:
                analysis_results.append({
                    "option_set": option_set,
                    "type": "different_high_convergence",
                    "description": f"All models converge strongly (>75%) but on different options",
                    "details": model_behaviors
                })
            elif prop_variance > 0.5:
                analysis_results.append({
                    "option_set": option_set,
                    "type": "high_variance",
                    "description": f"Large variance in convergence strength (diff: {prop_variance:.3f})",
                    "details": model_behaviors
                })
            elif all_same and prop_variance < 0.1:
                analysis_results.append({
                    "option_set": option_set,
                    "type": "consistent_behavior",
                    "description": f"All models show similar behavior, choosing {top_responses[0]}",
                    "details": model_behaviors
                })
    
    return analysis_results

if __name__ == "__main__":
    print("Extracting control condition distributions...")
    consolidated_data = extract_control_distributions()
    
    output_path = Path("/Users/graemeford/TBayLabs/silent_agreement/silent_agreement_v1/control_emoji_distributions.json")
    with open(output_path, 'w') as f:
        json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved consolidated data to {output_path}")
    
    print("\nAnalyzing variations...")
    analysis = analyze_variations(consolidated_data)
    
    analysis_output_path = Path("/Users/graemeford/TBayLabs/silent_agreement/silent_agreement_v1/control_behavior_analysis.json")
    with open(analysis_output_path, 'w') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"Saved analysis to {analysis_output_path}")
    
    print("\nInteresting findings:")
    for finding in analysis[:10]:
        print(f"\n{finding['option_set']}:")
        print(f"  Type: {finding['type']}")
        print(f"  {finding['description']}")
        if finding['type'] in ['different_high_convergence', 'high_variance']:
            for model, behavior in finding['details'].items():
                print(f"    {model}: {behavior['top_response']} ({behavior['top_proportion']:.1%})")