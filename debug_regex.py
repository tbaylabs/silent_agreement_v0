import re
import json

# Load options lists
with open('dataset_generation/options_lists/options_lists.json', 'r', encoding='utf-8') as f:
    options_lists = json.load(f)

# Get shapes_3|text which contains "hollow diamond"
valid_answers = options_lists["shapes_3|text"]
print("Valid answers:", valid_answers)

# Test different completions
test_completions = [
    "hollow diamond",
    "Hollow diamond",
    "hollow diamond ",
    " hollow diamond",
    " hollow diamond ",
    "hollow diamond\n",
    "\nhollow diamond",
    "hollow diamond.",
    "The answer is hollow diamond",
    "hollow\ndiamond",
    "hollow  diamond",  # double space
]

# Build regex pattern
pattern = '|'.join(re.escape(ans) for ans in valid_answers)
regex = rf'^\s*({pattern})\s*$'
print(f"\nRegex pattern: {regex}")
print(f"\nEscaped pattern parts:")
for ans in valid_answers:
    print(f"  '{ans}' -> '{re.escape(ans)}'")

print("\nTesting completions:")
for completion in test_completions:
    match = re.search(regex, completion)
    print(f"'{completion}' -> {'MATCH' if match else 'NO MATCH'}")
    if match:
        print(f"  Captured: '{match.group(1)}'")