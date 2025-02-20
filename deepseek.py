import os
import json
import subprocess

# Provider configuration as provided
provider_json = r'''
{
    "gpt-4o-mini": {
        "reasoning": false,
        "api_path": "default",
        "creator": "Open AI"
    },
    "deepseek-r1": {
        "reasoning": true,
        "api_path": "deepseek-reasoner",
        "openai_base_url": "https://api.deepseek.com",
        "creator": "DeepSeek"
    },
    "deepseek-v3": {
        "reasoning": false,
        "api_path": "deepseek-chat",
        "openai_base_url": "https://api.deepseek.com",
        "creator": "DeepSeek"
    }
}
'''

# Load the provider configuration
providers = json.loads(provider_json)

# Select the provider you want to use.
# For example, to use the deepseek-v3 provider:
selected_provider = "deepseek-v3"
provider_config = providers[selected_provider]

# Retrieve the DEEPSEEK_API_KEY from the environment
deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
if not deepseek_api_key:
    raise EnvironmentError("DEEPSEEK_API_KEY is not set in the environment.")

# Set the environment variables for the OpenAI-compatible API.
os.environ["OPENAI_API_KEY"] = deepseek_api_key
os.environ["OPENAI_BASE_URL"] = provider_config.get("openai_base_url", "https://api.openai.com/v1")

# (Optional) Print out the values to verify they are set correctly.
print("OPENAI_API_KEY:", os.environ["OPENAI_API_KEY"])
print("OPENAI_BASE_URL:", os.environ["OPENAI_BASE_URL"])

# Now run the benchmark.
# For example, assume you have a benchmark script "hello.py" and you want to run a single evaluation.
# Note: The model string is constructed as "openai/{provider}" because Inspect expects an OpenAI-compatible API.
command = [
    "inspect",
    "eval",
    "hello.py",
    "--model", f"deepseek/{selected_provider}",
    "--limit", "1"
]

print("Running benchmark command:", " ".join(command))
subprocess.run(command)