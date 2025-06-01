"""
Script to regenerate prompt hashes and documentation for both base and reasoning evaluations.

This script:
1. Generates and saves prompt hashes for both base and reasoning conditions
2. Creates markdown documentation files for both evaluation types
3. Verifies that the prompts match the saved hashes

Usage:
    python regenerate_hashes.py [--base-only] [--reasoning-only]
"""

import json
import hashlib
from typing import Dict, Any
from pathlib import Path
import argparse

from dataset_generation.base.base_conditions import (
    create_chat_messages,
    ExperimentCondition
)
from dataset_generation.reasoning.reasoning_conditions import (
    create_reasoning_chat_messages,
    ReasoningExperimentCondition,
    build_base_prompt as reasoning_build_base_prompt
)


# Placeholder options for generating sample prompts
PLACEHOLDER_OPTIONS = ["first_option", "second_option", "third_option", "fourth_option"]


def compute_prompt_hash(prompts: Dict[str, str]) -> str:
    """
    Compute a deterministic hash of a set of prompts.
    
    Args:
        prompts: Dictionary mapping condition names to prompt strings
        
    Returns:
        SHA-256 hash of the prompts
    """
    # Sort keys to ensure deterministic ordering
    sorted_prompts = {k: prompts[k] for k in sorted(prompts.keys())}
    
    # Create a canonical JSON representation
    canonical_json = json.dumps(sorted_prompts, sort_keys=True, ensure_ascii=True)
    
    # Compute SHA-256 hash
    return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()


def create_prompt_version_entry(prompts: Dict[str, str], timestamp: str) -> Dict[str, Any]:
    """
    Create a version entry for a set of prompts.
    
    Args:
        prompts: Dictionary of prompts by condition
        timestamp: ISO date string for when this version was created
        
    Returns:
        Version entry dictionary
    """
    return {
        "hash": compute_prompt_hash(prompts),
        "timestamp": timestamp,
        "prompts": prompts
    }


# =============================================================================
# BASE EVALUATION FUNCTIONS
# =============================================================================

def generate_base_sample_prompts() -> Dict[str, str]:
    """
    Generate sample prompts for all base conditions using placeholder options.
    
    Returns:
        Dict containing prompts for all three conditions.
    """
    # Generate experiment prompts (what the model sees)
    experiment_prompts = {}
    
    for condition in ExperimentCondition:
        # For experiment prompts, we just need the user message content
        messages = create_chat_messages(
            options=PLACEHOLDER_OPTIONS,
            condition=condition
        )
        # Extract just the user message content
        experiment_prompts[condition.value] = messages[0].content
    
    return experiment_prompts


def generate_and_save_base_prompt_hashes(output_path: Path = None) -> None:
    """
    Generate base sample prompts and save their hashes to a JSON file.
    
    Args:
        output_path: Path to save the JSON file
    """
    if output_path is None:
        output_path = Path(__file__).parent / "base" / "base_prompts_hashes.json"
    
    # Generate sample prompts
    prompts = generate_base_sample_prompts()
    
    # Create version entries
    timestamp = "2025-05-28"  # Original date for v1_standard
    
    prompt_hashes = {
        "experiment_prompts": {
            "v1_standard": create_prompt_version_entry(
                prompts=prompts,
                timestamp=timestamp
            )
        }
    }
    
    # Save to JSON file
    with open(output_path, 'w') as f:
        json.dump(prompt_hashes, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Base prompt hashes saved to: {output_path}")
    print(f"   Experiment prompts hash: {prompt_hashes['experiment_prompts']['v1_standard']['hash'][:16]}...")


def generate_base_prompt_documentation(input_path: Path = None, output_path: Path = None) -> None:
    """
    Generate markdown documentation for base evaluation prompts.
    
    Args:
        input_path: Path to the base_prompts_hashes.json file
        output_path: Path to save the markdown file
    """
    if input_path is None:
        input_path = Path(__file__).parent / "base" / "base_prompts_hashes.json"
    
    if output_path is None:
        output_path = Path(__file__).parent / "base" / "BASE_PROMPTS.md"
    
    # Load the prompt hashes
    with open(input_path) as f:
        prompt_data = json.load(f)
    
    # Start building the markdown content
    lines = [
        "# Silent Agreement Base Evaluation Prompts",
        "",
        "---",
        ""
    ]
    
    # Process experiment prompts
    lines.append("## Experiment Prompts")
    lines.append("")
    
    for version_name, version_data in prompt_data["experiment_prompts"].items():
        lines.append(f"### Version: {version_name}")
        lines.append("")
        lines.append(f"- **Created**: {version_data['timestamp']}")
        lines.append(f"- **Hash**: `{version_data['hash'][:16]}...`")
        lines.append("")
        
        # Add prompts for each condition
        for condition, prompt in version_data["prompts"].items():
            lines.append(f"#### {condition.replace('_', ' ').title()}")
            lines.append("")
            lines.append("```")
            lines.append(prompt)
            lines.append("```")
            lines.append("")
    
    # Write to file
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Base prompt documentation saved to: {output_path}")


# =============================================================================
# REASONING EVALUATION FUNCTIONS
# =============================================================================

def generate_reasoning_sample_prompts() -> Dict[str, str]:
    """
    Generate sample prompts for all reasoning conditions using placeholder options.
    
    Returns:
        Dict containing prompts for all three conditions.
    """
    prompts = {}
    
    for condition in ReasoningExperimentCondition:
        # For reasoning prompts, we just need the user message content
        messages = create_reasoning_chat_messages(
            options=PLACEHOLDER_OPTIONS,
            condition=condition
        )
        # Extract just the user message content
        prompts[condition.value] = messages[0].content
    
    return prompts


def generate_and_save_reasoning_prompt_hashes(output_path: Path = None) -> None:
    """
    Generate reasoning sample prompts and save their hashes to a JSON file.
    
    Args:
        output_path: Path to save the JSON file
    """
    if output_path is None:
        output_path = Path(__file__).parent / "reasoning" / "reasoning_prompts_hashes.json"
    
    # Generate sample prompts
    prompts = generate_reasoning_sample_prompts()
    
    # Create version entries
    timestamp = "2025-05-30"  # Original date for v1_reasoning
    
    prompt_hashes = {
        "reasoning_prompts": {
            "v1_reasoning": create_prompt_version_entry(
                prompts=prompts,
                timestamp=timestamp
            )
        }
    }
    
    # Save to JSON file
    with open(output_path, 'w') as f:
        json.dump(prompt_hashes, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Reasoning prompt hashes saved to: {output_path}")
    print(f"   Reasoning prompts hash: {prompt_hashes['reasoning_prompts']['v1_reasoning']['hash'][:16]}...")


def generate_reasoning_prompt_documentation(input_path: Path = None, output_path: Path = None) -> None:
    """
    Generate markdown documentation for reasoning evaluation prompts.
    
    Args:
        input_path: Path to the reasoning_prompts_hashes.json file
        output_path: Path to save the markdown file
    """
    if input_path is None:
        input_path = Path(__file__).parent / "reasoning" / "reasoning_prompts_hashes.json"
    
    if output_path is None:
        output_path = Path(__file__).parent / "reasoning" / "REASONING_PROMPTS.md"
    
    # Load the prompt hashes
    with open(input_path) as f:
        prompt_data = json.load(f)
    
    # Start building the markdown content
    lines = [
        "# Silent Agreement Reasoning Model Evaluation Prompts",
        "",
        "---",
        ""
    ]
    
    # Process reasoning prompts
    lines.append("## Reasoning Model Prompts")
    lines.append("")
    
    for version_name, version_data in prompt_data["reasoning_prompts"].items():
        lines.append(f"### Version: {version_name}")
        lines.append("")
        lines.append(f"- **Created**: {version_data['timestamp']}")
        lines.append(f"- **Hash**: `{version_data['hash'][:16]}...`")
        lines.append("")
        
        # Add prompts for each condition
        for condition, prompt in version_data["prompts"].items():
            lines.append(f"#### {condition.replace('_', ' ').title()}")
            lines.append("")
            lines.append("```")
            lines.append(prompt)
            lines.append("```")
            lines.append("")
    
    # Write to file
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Reasoning prompt documentation saved to: {output_path}")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Regenerate prompt hashes and documentation")
    parser.add_argument("--base-only", action="store_true", help="Only regenerate base evaluation files")
    parser.add_argument("--reasoning-only", action="store_true", help="Only regenerate reasoning evaluation files")
    args = parser.parse_args()
    
    # Determine what to regenerate
    do_base = not args.reasoning_only
    do_reasoning = not args.base_only
    
    if do_base:
        print("Regenerating base evaluation files...")
        print("=" * 60)
        
        # Generate and save base hashes
        generate_and_save_base_prompt_hashes()
        
        # Generate base documentation
        print("\nGenerating base prompt documentation...")
        generate_base_prompt_documentation()
        
        print()
    
    if do_reasoning:
        print("Regenerating reasoning evaluation files...")
        print("=" * 60)
        
        # Generate and save reasoning hashes
        generate_and_save_reasoning_prompt_hashes()
        
        # Generate reasoning documentation
        print("\nGenerating reasoning prompt documentation...")
        generate_reasoning_prompt_documentation()
        
        print()
    
    print("✅ All requested files have been regenerated successfully!")


if __name__ == "__main__":
    main()