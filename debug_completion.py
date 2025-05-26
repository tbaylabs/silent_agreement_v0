import re
import json

# Load options lists
with open('dataset_generation/options_lists/options_lists.json', 'r', encoding='utf-8') as f:
    options_lists = json.load(f)

# Function to debug a completion
def debug_completion(completion, option_id):
    valid_answers = options_lists[option_id]
    print(f"Option ID: {option_id}")
    print(f"Valid answers: {valid_answers}")
    
    # Build regex pattern
    pattern = '|'.join(re.escape(ans) for ans in valid_answers)
    regex = rf'^\s*({pattern})\s*$'
    
    print(f"\nCompletion: '{completion}'")
    print(f"Completion length: {len(completion)}")
    print(f"Completion repr: {repr(completion)}")
    print(f"Completion bytes: {completion.encode('utf-8')}")
    
    # Check for hidden characters
    print(f"\nCharacter analysis:")
    for i, char in enumerate(completion):
        print(f"  [{i}] '{char}' (ord: {ord(char)}, hex: {hex(ord(char))})")
    
    # Test match
    match = re.search(regex, completion)
    print(f"\nRegex match: {'YES' if match else 'NO'}")
    if match:
        print(f"Captured: '{match.group(1)}'")
    
    # Test case-insensitive match
    match_ci = re.search(regex, completion, re.IGNORECASE)
    print(f"Case-insensitive match: {'YES' if match_ci else 'NO'}")
    
    # Test each valid answer individually
    print(f"\nIndividual answer tests:")
    for ans in valid_answers:
        individual_regex = rf'^\s*{re.escape(ans)}\s*$'
        individual_match = re.search(individual_regex, completion)
        print(f"  '{ans}' -> {'MATCH' if individual_match else 'NO MATCH'}")

# Example: test "hollow diamond" against shapes_3|text
print("="*60)
debug_completion("hollow diamond", "shapes_3|text")

print("\n" + "="*60)
# Test with case variation
debug_completion("Hollow Diamond", "shapes_3|text")

print("\n" + "="*60)
# Test with extra punctuation
debug_completion("hollow diamond.", "shapes_3|text")