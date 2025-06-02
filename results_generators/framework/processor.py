"""
Abstract results processing framework.
Allows different evaluation types to have custom results processing.
"""

from abc import ABC, abstractmethod


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