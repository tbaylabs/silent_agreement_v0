import os
from inspect_ai.model import GenerateConfig
from inspect_ai.model._providers.openai import OpenAIAPI

class DeepseekModelAPI(OpenAIAPI):
    def __init__(
        self,
        model_name: str,
        base_url: str | None = None,
        api_key: str | None = None,
        config: GenerateConfig = GenerateConfig(),
        **model_args,
    ) -> None:
        # Set the base_url to DeepSeek's endpoint if not provided.
        base_url = base_url or "https://api.deepseek.com"
        # Get the API key from the DEEPSEEK_API_KEY environment variable.
        api_key = os.environ.get("DEEPSEEK_API_KEY", api_key)
        # Call the parent constructor with the correct arguments.
        super().__init__(model_name, base_url, api_key, config, **model_args)