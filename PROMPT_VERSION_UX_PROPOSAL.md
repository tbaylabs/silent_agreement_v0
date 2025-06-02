# Prompt Version Control - Detailed UX Proposal

## Overview
This document outlines the complete user experience for a Git-based prompt version control system, addressing all aspects of how users interact with prompt versions during evaluation runs.

## Key Design Decisions

### 1. Prompt Version Structure
- **Separate versions for each eval type**: Base, reasoning-effort, and reasoning-tokens have independent version tracking
- **Version format**: `base/v1`, `reasoning/v1`, etc.
- **Stored in**: `dataset_generation/PROMPT_VERSIONS.json`

### 2. What Gets Versioned
Each version tracks:
- Prompt template files (prompts.py, conditions.py)
- Constants used in prompts (from utils/constants.py)
- Git commit hash
- Timestamp
- Change description

## User Experience Flow

### Normal Evaluation Run (No Changes)

```bash
$ python scripts/run_eval.py --type base --model groq/llama-3.3-70b-versatile --test-mode quick-test

✅ Using prompt version: base/v1 (locked at commit abc123d)
Running Base evaluation for model: groq/llama-3.3-70b-versatile
Test mode: quick-test
...
[evaluation proceeds normally]
```

**Key Points**:
- Version displayed at start
- No interruption to workflow
- Version recorded in eval output file

### When Prompts Have Been Modified

```bash
$ python scripts/run_eval.py --type base --model groq/llama-3.3-70b-versatile --test-mode quick-test

⚠️  WARNING: Prompt files have been modified since base/v1!

Modified files:
  - dataset_generation/prompts.py (COORDINATION_PREFIX changed)
  
Current version: base/v1 (commit abc123d)
Your changes: uncommitted

Options:
1. Proceed with MODIFIED prompts (results will be marked as "base/v1-modified")
2. Create new version base/v2
3. Revert changes and use base/v1
4. Exit

Choose option (1-4): _
```

### Creating a New Version

If user selects option 2:

```bash
Choose option (1-4): 2

Creating new prompt version...

Please provide a description for base/v2: Updated coordination prefix for clarity

Summary of changes:
- COORDINATION_PREFIX: "coordinate with" → "coordinate your answer with"
- No other changes detected

Confirm creation of base/v2? (y/n): y

✅ Created new version: base/v2
✅ Updated PROMPT_VERSIONS.json
✅ Created git commit: "Prompt version base/v2: Updated coordination prefix for clarity"

Proceeding with evaluation using base/v2...
```

### Version Selection

Users can explicitly select versions:

```bash
# Use specific version
$ python scripts/run_eval.py --type base --model groq/llama --prompt-version base/v1

# Use latest version (default)
$ python scripts/run_eval.py --type base --model groq/llama

# List available versions
$ python scripts/run_eval.py --list-prompt-versions

Available prompt versions:
  base:
    - v1 (2024-05-28): Initial version
    - v2 (2024-06-03): Updated coordination prefix for clarity [LATEST]
  
  reasoning:
    - v1 (2024-05-28): Initial reasoning version [LATEST]
```

## Version Storage Format

### PROMPT_VERSIONS.json
```json
{
  "base": {
    "latest": "v2",
    "versions": {
      "v1": {
        "commit": "abc123def456",
        "timestamp": "2024-05-28T10:00:00Z",
        "description": "Initial version",
        "files_hash": "sha256:5b17eea59d30f7bf...",
        "constants": {
          "SUPPRESS_COT_SUFFIX": "Give only your answer and no other text.",
          "ELICIT_COT_SUFFIX": "Before answering, write..."
        }
      },
      "v2": {
        "commit": "def456ghi789",
        "timestamp": "2024-06-03T14:30:00Z",
        "description": "Updated coordination prefix for clarity",
        "files_hash": "sha256:6c28ffb60e40f8cf...",
        "constants": {
          "SUPPRESS_COT_SUFFIX": "Give only your answer and no other text.",
          "ELICIT_COT_SUFFIX": "Before answering, write..."
        }
      }
    }
  },
  "reasoning": {
    "latest": "v1",
    "versions": {
      "v1": {
        "commit": "ghi789jkl012",
        "timestamp": "2024-05-28T10:00:00Z",
        "description": "Initial reasoning version",
        "files_hash": "sha256:7d39ggc71f51g9dg...",
        "constants": {
          "LOW_REASONING_TOKENS": 4096,
          "HIGH_REASONING_TOKENS": 32768
        }
      }
    }
  }
}
```

## Evaluation Output Integration

### In Eval Files
```json
{
  "eval_name": "silent_agreement_task",
  "model": "groq/llama-3.3-70b-versatile",
  "prompt_version": "base/v2",
  "prompt_version_modified": false,
  "created": "2024-06-03T15:00:00Z",
  ...
}
```

### In Results
```json
{
  "experiment_results": {
    "metadata": {
      "prompt_version": "base/v2",
      "prompt_version_commit": "def456ghi789",
      "prompt_version_modified": false
    },
    ...
  }
}
```

## Hash Calculation Details

### What Gets Hashed
A single hash per eval type combining:
1. All prompt template strings (sorted deterministically)
2. All referenced constants (sorted by key)
3. The prompt assembly logic (via file hashes)

```python
def calculate_prompt_hash(eval_type: str) -> str:
    """Calculate hash for all prompts and constants for an eval type."""
    components = []
    
    # Add prompt templates
    if eval_type == "base":
        components.extend([
            ("COORDINATION_PREFIX", COORDINATION_PREFIX),
            ("SUPPRESS_COT_SUFFIX", SUPPRESS_COT_SUFFIX),
            # ... all other constants
        ])
        # Add file hashes for prompt assembly files
        components.append(("file:prompts.py", hash_file("dataset_generation/prompts.py")))
        components.append(("file:base_conditions.py", hash_file("dataset_generation/base/base_conditions.py")))
    
    # Sort for deterministic ordering
    components.sort(key=lambda x: x[0])
    
    # Create JSON representation and hash
    json_str = json.dumps(components, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()
```

## Independence Between Eval Types

- **Separate versioning**: Changing base prompts doesn't affect reasoning versions
- **Separate hash calculation**: Each eval type has its own hash
- **Can evolve independently**: Base might be at v5 while reasoning is still at v1

## CLI Integration

### New Arguments
```bash
--prompt-version VERSION     Use specific prompt version (default: latest)
--list-prompt-versions      List all available prompt versions
--create-prompt-version     Create new version from current changes
--allow-modified           Allow running with modified prompts
```

### Environment Variable
```bash
# Always use v1 for regression testing
export SA_PROMPT_VERSION=base/v1
```

## Benefits of This Approach

1. **Clear Communication**: Users always know what version they're running
2. **Flexible Workflow**: Can experiment with modifications or create proper versions
3. **Full Traceability**: Every eval result includes exact prompt version
4. **Independent Evolution**: Different eval types can progress at different rates
5. **Simple Recovery**: Easy to revert to any previous version
6. **Git Integration**: Leverages Git's power while adding user-friendly layer

## Migration Path

1. Generate initial versions from current prompts
2. Mark current experiments with appropriate versions
3. Update documentation with version information
4. Add version checking to eval scripts
5. Deprecate old hash system once stable