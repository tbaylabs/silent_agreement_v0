"""
Prompt hashing and versioning system for reasoning model evaluations.
Ensures consistency of prompts across evaluations by computing and verifying hashes.
"""

import json
import hashlib
from typing import Dict, Any
from pathlib import Path

from dataset_generation.reasoning.reasoning_conditions import (
    create_reasoning_chat_messages,
    ReasoningExperimentCondition,
    build_base_prompt
)


# Placeholder options for generating sample prompts
PLACEHOLDER_OPTIONS = ["first_option", "second_option", "third_option", "fourth_option"]


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


def generate_and_save_reasoning_prompt_hashes(output_path: Path = None) -> None:
    """
    Generate reasoning sample prompts and save their hashes to a JSON file.
    
    Args:
        output_path: Path to save the JSON file (defaults to reasoning_prompts_hashes.json
                    in the reasoning directory)
    """
    if output_path is None:
        output_path = Path(__file__).parent / "reasoning_prompts_hashes.json"
    
    # Generate sample prompts
    prompts = generate_reasoning_sample_prompts()
    
    # Create version entries
    timestamp = "2025-05-30"  # Today's date for v1_reasoning
    
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


def verify_reasoning_prompt_version(version: str = "v1_reasoning") -> bool:
    """
    Verify that current reasoning prompts match the specified version.
    
    Args:
        version: Version name to check against
        
    Returns:
        True if prompts match, False otherwise
        
    Raises:
        RuntimeError: If verification fails with details
    """
    # Load saved hashes
    hash_file = Path(__file__).parent / "reasoning_prompts_hashes.json"
    
    if not hash_file.exists():
        raise RuntimeError(
            f"Reasoning prompt hash file not found: {hash_file}\n"
            "Run generate_and_save_reasoning_prompt_hashes() to create it."
        )
    
    with open(hash_file) as f:
        saved_hashes = json.load(f)
    
    # Generate current prompts
    current_prompts = generate_reasoning_sample_prompts()
    
    # Check reasoning prompts
    if version not in saved_hashes["reasoning_prompts"]:
        raise RuntimeError(f"Unknown reasoning prompt version: {version}")
    
    saved_hash = saved_hashes["reasoning_prompts"][version]["hash"]
    current_hash = compute_prompt_hash(current_prompts)
    
    if saved_hash != current_hash:
        raise RuntimeError(
            f"Reasoning prompts have changed!\n"
            f"Expected hash ({version}): {saved_hash[:16]}...\n"
            f"Current hash:              {current_hash[:16]}...\n"
            f"This likely means the prompt templates have been modified.\n"
            f"If this is intentional, create a new version in reasoning_prompts_hashes.json"
        )
    
    return True


if __name__ == "__main__":
    # Generate and save the v1_reasoning hashes
    generate_and_save_reasoning_prompt_hashes()
    
    # Verify they work
    print("\nVerifying reasoning prompt versions...")
    try:
        verify_reasoning_prompt_version("v1_reasoning")
        print("✅ Reasoning prompt verification successful!")
    except RuntimeError as e:
        print(f"❌ Reasoning prompt verification failed: {e}")