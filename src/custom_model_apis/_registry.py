from inspect_ai.model import modelapi

@modelapi("deepseek")
def deepseek():
    from .custom import DeepseekModelAPI
    return DeepseekModelAPI