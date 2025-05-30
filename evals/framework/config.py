"""
Abstract evaluation configuration framework.
Defines the interface for different evaluation types.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable
from inspect_ai import Task


class EvalConfig(ABC):
    """Abstract base class for evaluation configurations."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the name of this evaluation type."""
        pass
    
    @abstractmethod
    def parse_args(self, args: List[str]) -> Dict[str, Any]:
        """
        Parse command line arguments specific to this evaluation type.
        
        Args:
            args: List of command line arguments
            
        Returns:
            Dictionary of parsed arguments
        """
        pass
    
    @abstractmethod
    def get_eval_params(self, parsed_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get evaluation parameters for the task.
        
        Args:
            parsed_args: Parsed command line arguments
            
        Returns:
            Dictionary of parameters to pass to the task
        """
        pass
    
    @abstractmethod
    def get_task_factory(self) -> Callable:
        """
        Get the task factory function for this evaluation type.
        
        Returns:
            Callable that creates the inspect-ai Task
        """
        pass
    
    @abstractmethod
    def validate_setup(self, parsed_args: Dict[str, Any]) -> None:
        """
        Validate the evaluation setup (e.g., prompt versions, dependencies).
        
        Args:
            parsed_args: Parsed command line arguments
            
        Raises:
            RuntimeError: If validation fails
        """
        pass
    
    @abstractmethod
    def get_results_processor(self, parsed_args: Dict[str, Any]) -> Callable:
        """
        Get the results processor for this evaluation type.
        
        Args:
            parsed_args: Parsed command line arguments
            
        Returns:
            Callable that processes evaluation results
        """
        pass
    
    def supports_test_mode(self) -> bool:
        """Return whether this evaluation type supports test modes."""
        return True
    
    def get_reasoning_config(self, model_name: str, parsed_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get reasoning configuration for thinking models.
        
        Args:
            model_name: Name of the model being evaluated
            parsed_args: Parsed command line arguments
            
        Returns:
            Dictionary of reasoning parameters for inspect-ai
        """
        return {}