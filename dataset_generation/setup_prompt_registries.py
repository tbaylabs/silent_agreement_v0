#!/usr/bin/env python3
"""
Setup script to create prompt registries for different evaluation types.
"""

from pathlib import Path
from dataset_generation.prompt_registry import PromptRegistry
from dataset_generation.chat_message_builder import ExperimentCondition, create_chat_messages
from dataset_generation.thinking_conditions import ThinkingExperimentCondition, create_thinking_chat_messages


def setup_base_prompts():
    """Set up base evaluation prompt registry."""
    print("Setting up base prompt registry...")
    
    # Use existing file location for backward compatibility
    registry_file = Path(__file__).parent / "sample_prompts_hashes.json"
    
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


def setup_thinking_prompts():
    """Set up thinking model prompt registry."""
    print("\\nSetting up thinking prompt registry...")
    
    registry_file = Path(__file__).parent / "thinking_prompts_hashes.json"
    
    thinking_registry = PromptRegistry(
        registry_file=str(registry_file),
        condition_enum=ThinkingExperimentCondition,
        prompt_name="thinking_prompts",
        message_factory=create_thinking_chat_messages
    )
    
    # Save the v1_thinking version
    thinking_registry.save_version("v1_thinking", "2025-05-30")
    
    # Verify it works
    try:
        thinking_registry.verify_version("v1_thinking")
        print("✅ Thinking prompts verified successfully!")
    except RuntimeError as e:
        print(f"⚠️  Thinking prompt verification issue: {e}")


def main():
    setup_base_prompts()
    setup_thinking_prompts()
    print("\\n✅ All prompt registries set up successfully!")


if __name__ == "__main__":
    main()