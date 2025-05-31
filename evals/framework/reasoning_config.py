"""
Abstract configuration for reasoning model evaluations.
Provides the base class for both token-based and effort-based reasoning evals.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Type
from enum import Enum

from evals.framework.config import EvalConfig
from dataset_generation.reasoning.reasoning_conditions import ReasoningExperimentCondition


class ReasoningEvalConfig(EvalConfig, ABC):
    """Abstract base class for reasoning model evaluation configurations."""
    
    def get_name(self) -> str:
        return "reasoning model evaluation"
    
    def get_condition_enum(self) -> Type[Enum]:
        """Get the condition enum for reasoning evaluations."""
        return ReasoningExperimentCondition
    
    @abstractmethod
    def get_reasoning_params(self) -> Dict[str, Dict[str, Any]]:
        """
        Get reasoning parameters for each condition.
        
        Returns:
            Dict mapping condition names to their reasoning parameters.
            E.g., {"control": {"reasoning_tokens": 4096}, ...}
        """
        pass
    
    @abstractmethod
    def get_reasoning_type(self) -> str:
        """
        Get the type of reasoning parameters this config uses.
        
        Returns:
            Either "tokens" or "effort"
        """
        pass
    
    def validate_model_support(self, model_name: str) -> None:
        """
        Validate that the model supports the reasoning parameters this config uses.
        
        Args:
            model_name: The model to validate
            
        Raises:
            ValueError: If model doesn't support the required reasoning parameters
        """
        from dataset_generation.model_prompt_registries import detect_model_family, ModelFamily
        
        family = detect_model_family(model_name)
        reasoning_type = self.get_reasoning_type()
        
        if reasoning_type == "tokens" and family != ModelFamily.REASONING:
            raise ValueError(
                f"Model {model_name} (family: {family.value}) does not support reasoning_tokens. "
                f"Use effort-based evaluation for this model or try a Claude 3.7+ model."
            )
        elif reasoning_type == "effort" and family != ModelFamily.EFFORT_BASED:
            raise ValueError(
                f"Model {model_name} (family: {family.value}) does not support reasoning_effort. "
                f"Use token-based evaluation for this model or try an OpenAI o-series model."
            )