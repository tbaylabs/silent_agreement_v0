#!/usr/bin/env python3
"""
Token-based reasoning evaluation runner.
For models that support reasoning_tokens parameter (Claude 3.7+, Gemini 2.5+).
"""

import sys
from evals.framework.runner import EvalRunner
from evals.reasoning.token_reasoning_config import TokenReasoningEvalConfig


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help']:
        config = TokenReasoningEvalConfig()
        config._print_help()
        sys.exit(1)
    
    model_name = sys.argv[1]
    args = sys.argv[2:]  # Arguments after model name
    
    # Create configuration and runner
    config = TokenReasoningEvalConfig()
    
    # Validate model supports token-based reasoning
    try:
        config.validate_model_support(model_name)
    except ValueError as e:
        print(f"❌ Model validation failed: {e}")
        sys.exit(1)
    
    runner = EvalRunner(config)
    
    # Run the evaluation
    runner.run(model_name, args)


if __name__ == "__main__":
    main()