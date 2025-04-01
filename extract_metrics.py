#!/usr/bin/env python3
import json
import os
import glob
import re

def extract_model_name(path):
    # Extract model name from path like results/claude-3-5-sonnet-20241022/20250222_140448/stats_overview.json
    parts = path.split(os.sep)
    if len(parts) >= 2:
        return parts[-3]  # Get the model name folder
    return "unknown"

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
            
            # Extract the top_prop_include_invalid object
            if 'absolute_metrics' in data and 'top_prop_include_invalid' in data['absolute_metrics']:
                results[model_name] = data['absolute_metrics']['top_prop_include_invalid']
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
    
    # Write results to a new JSON file
    output_file = 'model_metrics.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Extracted metrics saved to {output_file}")

if __name__ == "__main__":
    main()