"""Test script to verify DeepSeek model registration."""

from inspect_ai.model import get_model
from unsupported_model_providers.deepseek.model_registry import register_deepseek_models

def test_registration():
    """Test that DeepSeek models can be registered and accessed."""
    # Register the models
    register_deepseek_models()
    
    try:
        # Try to get a DeepSeek model
        model = get_model("deepseek/deepseek-chat")
        print("✅ Successfully registered and accessed DeepSeek model")
        print(f"Model name: {model.name}")
        print(f"Model API type: {type(model.api).__name__}")
        return True
    except Exception as e:
        print("❌ Failed to register/access DeepSeek model")
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_registration()
