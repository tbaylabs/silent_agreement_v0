#!/usr/bin/env python3
"""
Setup script to create prompt registries for different evaluation types.
"""

from pathlib import Path
from dataset_generation.prompt_registry import PromptRegistry
from dataset_generation.base.base_conditions import ExperimentCondition, create_chat_messages
from dataset_generation.reasoning.reasoning_conditions import ReasoningExperimentCondition, create_reasoning_chat_messages


def setup_base_prompts():
    """Set up base evaluation prompt registry."""
    print("Setting up base prompt registry...")
    
    # Use new file location in base folder
    registry_file = Path(__file__).parent / "base" / "base_prompts_hashes.json"
    
    base_registry = PromptRegistry(
        registry_file=str(registry_file),
        condition_enum=ExperimentCondition,
        prompt_name="experiment_prompts",
        message_factory=create_chat_messages
    )
    
    # Save the v1_standard version (should match existing)
    base_registry.save_version("v1_standard", "2025-05-28")
    
    # Verify it matches
    try:
        base_registry.verify_version("v1_standard")
        print("✅ Base prompts verified successfully!")
    except RuntimeError as e:
        print(f"⚠️  Base prompt verification issue: {e}")


def setup_reasoning_prompts():
    """Set up reasoning model prompt registry."""
    print("\\nSetting up reasoning prompt registry...")
    
    registry_file = Path(__file__).parent / "reasoning" / "reasoning_prompts_hashes.json"
    
    reasoning_registry = PromptRegistry(
        registry_file=str(registry_file),
        condition_enum=ReasoningExperimentCondition,
        prompt_name="reasoning_prompts",
        message_factory=create_reasoning_chat_messages
    )
    
    # Save the v1_reasoning version
    reasoning_registry.save_version("v1_reasoning", "2025-05-30")
    
    # Verify it works
    try:
        reasoning_registry.verify_version("v1_reasoning")
        print("✅ Reasoning prompts verified successfully!")
    except RuntimeError as e:
        print(f"⚠️  Reasoning prompt verification issue: {e}")


def main():
    setup_base_prompts()
    setup_reasoning_prompts()
    print("\\n✅ All prompt registries set up successfully!")


if __name__ == "__main__":
    main()