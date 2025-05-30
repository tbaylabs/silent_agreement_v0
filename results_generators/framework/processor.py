"""
Abstract results processing framework.
Allows different evaluation types to have custom results processing.
"""

from abc import ABC, abstractmethod
from typing import List, Any
from inspect_ai.dataset import Sample


class ResultsProcessor(ABC):
    """Abstract base class for results processing."""
    
    @abstractmethod
    def generate_results(self, eval_file: str, force_overwrite: bool = False) -> bool:
        """
        Generate results from an evaluation file.
        
        Args:
            eval_file: Path to the .eval file
            force_overwrite: Whether to overwrite existing results
            
        Returns:
            True if successful, False otherwise
        """
        pass


class BaseResultsProcessor(ResultsProcessor):
    """Results processor for base Silent Agreement evaluations."""
    
    def generate_results(self, eval_file: str, force_overwrite: bool = False) -> bool:
        """Generate results using the standard base eval pipeline."""
        from results_generators.generate_json_results import generate_json_results_from_eval
        return generate_json_results_from_eval(eval_file, force_overwrite)


class ThinkingResultsProcessor(ResultsProcessor):
    """Results processor for thinking model evaluations."""
    
    def __init__(self, control_samples: List[Sample]):
        """
        Initialize with control samples from base evaluation.
        
        Args:
            control_samples: Control condition samples from base eval
        """
        self.control_samples = control_samples
    
    def generate_results(self, eval_file: str, force_overwrite: bool = False) -> bool:
        """
        Generate results combining thinking samples with reused control data.
        
        This will implement the thinking-specific results generation logic
        that combines the new thinking condition samples with the reused
        control samples to create thinking vs control comparisons.
        """
        # TODO: Implement thinking-specific results generation
        # This would:
        # 1. Load thinking samples from eval_file
        # 2. Combine with self.control_samples
        # 3. Generate thinking-specific metrics (thinking_basic vs control, thinking_ultra vs control)
        # 4. Create thinking-specific reports
        
        print("⚠️  Thinking results processor not yet implemented")
        print("   This will combine thinking samples with reused control data")
        return False