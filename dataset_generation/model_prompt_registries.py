"""
Model-specific prompt registry helpers.
Manages different prompt types for different reasoning model families.
"""

from pathlib import Path
from typing import Dict, Type
from enum import Enum

from dataset_generation.prompt_registry import PromptRegistry
from dataset_generation.base.base_conditions import ExperimentCondition, create_chat_messages
from dataset_generation.reasoning.reasoning_conditions import ReasoningExperimentCondition, create_reasoning_chat_messages


class ModelFamily(Enum):
    """Different reasoning model families with different prompt needs."""
    BASE = "base"                    # Non-reasoning models (original base eval)
    REASONING = "reasoning"          # Models with reasoning capabilities (Claude 3.7, o-series)
    EFFORT_BASED = "effort_based"    # Models with reasoning_effort parameter (OpenAI o-series)


def get_prompt_registry(model_family: ModelFamily, base_dir: str = None) -> PromptRegistry:
    """
    Get the appropriate prompt registry for a model family.
    
    Args:
        model_family: The model family type
        base_dir: Base directory for registry files (defaults to current directory)
        
    Returns:
        PromptRegistry configured for the model family
    """
    if base_dir is None:
        base_dir = Path(__file__).parent
    else:
        base_dir = Path(base_dir)
    
    if model_family == ModelFamily.BASE:
        return PromptRegistry(
            registry_file=str(base_dir / "base" / "base_prompts_hashes.json"),
            condition_enum=ExperimentCondition,
            prompt_name="experiment_prompts",
            message_factory=create_chat_messages
        )
    
    elif model_family == ModelFamily.REASONING:
        return PromptRegistry(
            registry_file=str(base_dir / "reasoning" / "reasoning_prompts_hashes.json"),
            condition_enum=ReasoningExperimentCondition,
            prompt_name="reasoning_prompts",
            message_factory=create_reasoning_chat_messages
        )
    
    elif model_family == ModelFamily.EFFORT_BASED:
        # TODO: Implement effort-based prompts for OpenAI o-series
        raise NotImplementedError("Effort-based prompts not yet implemented")
    
    else:
        raise ValueError(f"Unknown model family: {model_family}")


def detect_model_family(model_name: str) -> ModelFamily:
    """
    Detect the model family from the model name.
    
    Args:
        model_name: Full model name (e.g., "anthropic/claude-3-7-sonnet-20250219")
        
    Returns:
        ModelFamily enum value
    """
    model_lower = model_name.lower()
    
    # Claude 3.7 and later reasoning models
    if "claude-3-7" in model_lower or "claude-4" in model_lower:
        return ModelFamily.REASONING
    
    # OpenAI o-series models  
    elif any(pattern in model_lower for pattern in ["openai/o1", "openai/o3", "openai/o4", "/o1-", "/o3-", "/o4-"]):
        return ModelFamily.EFFORT_BASED
    
    # Default to base for all other models
    else:
        return ModelFamily.BASE


def verify_model_prompts(model_name: str, version: str = None) -> bool:
    """
    Verify prompts for a specific model.
    
    Args:
        model_name: Full model name
        version: Prompt version to verify (uses default if None)
        
    Returns:
        True if verification succeeds
    """
    family = detect_model_family(model_name)
    registry = get_prompt_registry(family)
    
    if version is None:
        if family == ModelFamily.BASE:
            version = "v1_standard"
        elif family == ModelFamily.REASONING:
            version = "v1_reasoning"
        else:
            raise ValueError(f"No default version for {family}")
    
    return registry.verify_version(version)


def list_available_models() -> Dict[ModelFamily, Dict[str, str]]:
    """
    List all available model families and their prompt versions.
    
    Returns:
        Dictionary mapping model families to their available versions
    """
    available = {}
    
    for family in ModelFamily:
        try:
            if family == ModelFamily.EFFORT_BASED:
                available[family] = {"status": "not_implemented"}
                continue
                
            registry = get_prompt_registry(family)
            versions = registry.list_versions()
            
            if versions:
                available[family] = {
                    "versions": versions,
                    "latest_hash": registry.get_version_info(versions[0])["hash"][:16] + "..."
                }
            else:
                available[family] = {"status": "no_versions"}
                
        except Exception as e:
            available[family] = {"status": f"error: {e}"}
    
    return available


if __name__ == "__main__":
    print("Model Prompt Registries Status:")
    print("=" * 40)
    
    available = list_available_models()
    for family, info in available.items():
        print(f"\\n{family.value.upper()}:")
        if "versions" in info:
            print(f"  Versions: {', '.join(info['versions'])}")
            print(f"  Latest hash: {info['latest_hash']}")
        else:
            print(f"  Status: {info['status']}")
    
    print("\\nModel Family Detection Examples:")
    test_models = [
        "anthropic/claude-3-5-sonnet-20241022",
        "anthropic/claude-3-7-sonnet-20250219", 
        "openai/o1-preview",
        "openai/gpt-4o",
        "groq/llama-3.3-70b-versatile"
    ]
    
    for model in test_models:
        family = detect_model_family(model)
        print(f"  {model} -> {family.value}")