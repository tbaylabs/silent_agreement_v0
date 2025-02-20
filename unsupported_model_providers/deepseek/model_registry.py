"""Register DeepSeek models with the inspect library."""

from inspect_ai._util.registry import registry_register

def register_deepseek_models():
    """Register DeepSeek models with the inspect library."""
    registry_register(
        "modelapi",
        "deepseek",
        "inspect_ai.model.openai.OpenAIModelAPI",
        description="DeepSeek API (OpenAI-compatible)"
    )
