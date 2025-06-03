"""
Reasoning model allowlist and configuration.

WARNING: Reasoning models can be VERY expensive to run!
Always use quick-test mode first to verify your code works before running full evaluations.

The costs can be substantial:
- OpenAI o-series models can cost $15-60 per 1M tokens
- Claude 3.7 Sonnet with extended thinking can be expensive
- Always check current pricing before running evaluations
"""

# Allowlists for each reasoning evaluation type
# Models must be explicitly added here to be allowed to run reasoning evaluations
REASONING_MODELS = {
    "tokens": {
        # Models that support reasoning_tokens parameter
        # Examples: Claude 3.7+, Gemini 2.5+, DeepSeek R1
        "groq/llama-3.3-70b-versatile",  # TEST MODEL ONLY - not actually a reasoning model
        # Add real models here when ready:
        # "anthropic/claude-3-7-sonnet-20250219",
        # "anthropic/claude-3-7-sonnet-latest", 
        # "google/gemini-2.5-flash-preview-05-20",
        # "google/gemini-2.5-pro-preview-05-06",
        # "together/deepseek-ai/DeepSeek-R1",
        # "groq/deepseek-r1-distill-llama-70b",
    },
    "effort": {
        # Models that support reasoning_effort parameter
        # Examples: OpenAI o-series, Grok
        "groq/llama-3.3-70b-versatile",  # TEST MODEL ONLY - not actually a reasoning model
        # Add real models here when ready:
        # "openai/o3-mini",
        # "openai/o4-mini",
        # "openai/o4-mini-2025-04-16",
        # "grok/grok-3-mini-beta",
        # "grok/grok-3-fast-beta",
    },
    "prompt": {
        # Reasoning models without special parameters
        # Models that do reasoning but don't expose effort/tokens parameters
        "groq/llama-3.3-70b-versatile",  # TEST MODEL ONLY - not actually a reasoning model
        # Add real models here when ready:
        # "ollama/deepseek-r1:latest",
        # Other reasoning models that use prompt-only approach
    }
}

def is_model_allowed(model: str, eval_type: str) -> bool:
    """
    Check if a model is allowed for a specific reasoning evaluation type.
    
    Args:
        model: Model identifier (e.g., "openai/o4-mini")
        eval_type: Evaluation type ("tokens", "effort", or "prompt")
        
    Returns:
        True if model is in the allowlist for this eval type
    """
    if eval_type not in REASONING_MODELS:
        return False
    
    return model in REASONING_MODELS[eval_type]

def get_allowed_models(eval_type: str) -> set:
    """
    Get the set of allowed models for a specific evaluation type.
    
    Args:
        eval_type: Evaluation type ("tokens", "effort", or "prompt")
        
    Returns:
        Set of allowed model identifiers
    """
    return REASONING_MODELS.get(eval_type, set())

def check_model_allowed(model: str, eval_type: str):
    """
    Check if a model is allowed and raise an error if not.
    
    Args:
        model: Model identifier
        eval_type: Evaluation type
        
    Raises:
        ValueError: If model is not in the allowlist
    """
    if not is_model_allowed(model, eval_type):
        allowed = get_allowed_models(eval_type)
        raise ValueError(
            f"\n❌ Model '{model}' is not in the allowlist for {eval_type} reasoning evaluation.\n"
            f"\nAllowed models for {eval_type} evaluation:\n"
            + "\n".join(f"  - {m}" for m in sorted(allowed))
            + "\n\nTo add a new model:"
            + f"\n1. Edit utils/reasoning_models.py"
            + f"\n2. Add '{model}' to REASONING_MODELS['{eval_type}']"
            + "\n3. Be aware that reasoning models can be VERY expensive!"
            + "\n4. Always test with quick-test mode first"
        )