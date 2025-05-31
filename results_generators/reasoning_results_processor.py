"""
Results processor for reasoning model evaluations.
Handles processing and analysis of reasoning evaluation results.
"""

from typing import Dict, Any
from pathlib import Path
import json

from results_generators.generate_json_results import generate_json_results_from_eval
from results_generators.markdown_report_generator import generate_markdown_report


class ReasoningResultsProcessor:
    """Processes results from reasoning model evaluations."""
    
    def __init__(self, reasoning_type: str):
        """
        Initialize the processor.
        
        Args:
            reasoning_type: Either "tokens" or "effort"
        """
        self.reasoning_type = reasoning_type
    
    def process_results(self, eval_file_path: str, force_overwrite: bool = False) -> bool:
        """
        Process reasoning evaluation results.
        
        Args:
            eval_file_path: Path to the .eval file
            force_overwrite: Whether to overwrite existing results
            
        Returns:
            True if processing succeeded, False otherwise
        """
        try:
            # Generate standard JSON results first
            success = generate_json_results_from_eval(eval_file_path, force_overwrite=force_overwrite)
            if not success:
                return False
            
            # Generate reasoning-specific analysis
            self._generate_reasoning_analysis(eval_file_path)
            
            return True
            
        except Exception as e:
            print(f"Error processing reasoning results: {e}")
            return False
    
    def _generate_reasoning_analysis(self, eval_file_path: str) -> None:
        """Generate reasoning-specific analysis and reports."""
        eval_dir = Path(eval_file_path).parent
        
        # Load the generated experiment results
        experiment_results_path = eval_dir / "experiment_results.json"
        if not experiment_results_path.exists():
            print("Warning: No experiment_results.json found for reasoning analysis")
            return
        
        with open(experiment_results_path) as f:
            experiment_results = json.load(f)
        
        # Extract reasoning-specific metrics
        reasoning_metrics = self._extract_reasoning_metrics(experiment_results)
        
        # Save reasoning analysis
        reasoning_analysis_path = eval_dir / "reasoning_analysis.json"
        with open(reasoning_analysis_path, 'w') as f:
            json.dump(reasoning_metrics, f, indent=2)
        
        print(f"✅ Reasoning analysis saved to: {reasoning_analysis_path}")
    
    def _extract_reasoning_metrics(self, experiment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract reasoning-specific metrics from experiment results."""
        reasoning_metrics = {
            "reasoning_type": self.reasoning_type,
            "coordination_improvement": {},
            "reasoning_efficiency": {},
            "condition_performance": {}
        }
        
        # Extract coordination improvement metrics
        if "difference_metrics" in experiment_results:
            diff_metrics = experiment_results["difference_metrics"].get("top_prop_exclude_invalid", {})
            symbol_and_text = diff_metrics.get("symbol_and_text", {})
            
            # Coordination improvement over control
            coordinate_only_vs_control = symbol_and_text.get("coordinate_only_vs_control", {})
            coordinate_elicit_vs_control = symbol_and_text.get("coordinate_elicit_thought_vs_control", {})
            
            reasoning_metrics["coordination_improvement"] = {
                "basic_reasoning_improvement": {
                    "mean": coordinate_only_vs_control.get("mean"),
                    "significant": coordinate_only_vs_control.get("one_tail_significant", False),
                    "p_value": coordinate_only_vs_control.get("one_tail_p_value")
                },
                "elicited_reasoning_improvement": {
                    "mean": coordinate_elicit_vs_control.get("mean"),
                    "significant": coordinate_elicit_vs_control.get("one_tail_significant", False),
                    "p_value": coordinate_elicit_vs_control.get("one_tail_p_value")
                }
            }
            
            # Reasoning elicitation effect
            coordinate_elicit_vs_basic = symbol_and_text.get("coordinate_elicit_thought_vs_coordinate_only", {})
            reasoning_metrics["reasoning_efficiency"] = {
                "elicitation_effect": {
                    "mean": coordinate_elicit_vs_basic.get("mean"),
                    "significant": coordinate_elicit_vs_basic.get("one_tail_significant", False),
                    "p_value": coordinate_elicit_vs_basic.get("one_tail_p_value")
                }
            }
        
        # Extract absolute performance by condition
        if "absolute_metrics" in experiment_results:
            abs_metrics = experiment_results["absolute_metrics"].get("top_prop_exclude_invalid", {})
            symbol_and_text = abs_metrics.get("symbol_and_text", {})
            
            reasoning_metrics["condition_performance"] = {
                "control": symbol_and_text.get("control_stats", {}),
                "coordinate_only": symbol_and_text.get("ooc_coordinate_stats", {}),  # Mapped from base
                "coordinate_elicit_thought": symbol_and_text.get("cot_coordinate_stats", {})  # Mapped from base
            }
        
        return reasoning_metrics
    
    def generate_reasoning_report(self, eval_file_path: str) -> None:
        """Generate a reasoning-specific markdown report."""
        eval_dir = Path(eval_file_path).parent
        
        # Check if reasoning analysis exists
        reasoning_analysis_path = eval_dir / "reasoning_analysis.json"
        if not reasoning_analysis_path.exists():
            print("Warning: No reasoning analysis found. Run process_results first.")
            return
        
        with open(reasoning_analysis_path) as f:
            reasoning_metrics = json.load(f)
        
        # Generate reasoning-specific report content
        report_lines = [
            f"# Reasoning Model Evaluation Report ({self.reasoning_type.title()}-Based)",
            "",
            "## Reasoning Performance Summary",
            ""
        ]
        
        # Add coordination improvement summary
        coord_improvement = reasoning_metrics.get("coordination_improvement", {})
        basic_improvement = coord_improvement.get("basic_reasoning_improvement", {})
        elicit_improvement = coord_improvement.get("elicited_reasoning_improvement", {})
        
        if basic_improvement.get("mean") is not None:
            report_lines.extend([
                f"- **Basic Reasoning Coordination**: {basic_improvement['mean']:.3f} improvement over control",
                f"  - Statistically significant: {basic_improvement.get('significant', False)}"
            ])
        
        if elicit_improvement.get("mean") is not None:
            report_lines.extend([
                f"- **Elicited Reasoning Coordination**: {elicit_improvement['mean']:.3f} improvement over control", 
                f"  - Statistically significant: {elicit_improvement.get('significant', False)}"
            ])
        
        # Add reasoning efficiency summary
        reasoning_efficiency = reasoning_metrics.get("reasoning_efficiency", {})
        elicitation_effect = reasoning_efficiency.get("elicitation_effect", {})
        
        if elicitation_effect.get("mean") is not None:
            report_lines.extend([
                "",
                "## Reasoning Elicitation Effect",
                f"- **Elicitation vs Basic Reasoning**: {elicitation_effect['mean']:.3f} difference",
                f"  - Statistically significant: {elicitation_effect.get('significant', False)}"
            ])
        
        # Write reasoning report
        reasoning_report_path = eval_dir / "reasoning_report.md"
        with open(reasoning_report_path, 'w') as f:
            f.write('\n'.join(report_lines))
        
        print(f"✅ Reasoning report saved to: {reasoning_report_path}")


def generate_reasoning_results_from_eval(eval_file_path: str, reasoning_type: str, force_overwrite: bool = False) -> bool:
    """
    Convenience function to process reasoning evaluation results.
    
    Args:
        eval_file_path: Path to the .eval file
        reasoning_type: Either "tokens" or "effort"  
        force_overwrite: Whether to overwrite existing results
        
    Returns:
        True if processing succeeded, False otherwise
    """
    processor = ReasoningResultsProcessor(reasoning_type)
    success = processor.process_results(eval_file_path, force_overwrite)
    
    if success:
        processor.generate_reasoning_report(eval_file_path)
    
    return success