"""Register DeepSeek models with the inspect library."""

from inspect_ai._util.registry import Registry

def register_deepseek_models():
    """Register DeepSeek models with the inspect library."""
    Registry.register(
        type="modelapi",
        name="deepseek",
        value="inspect_ai.model.openai.OpenAIModelAPI",
        description="DeepSeek API (OpenAI-compatible)"
    )
