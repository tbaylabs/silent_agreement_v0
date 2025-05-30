#!/usr/bin/env python3
"""
Refactored base evaluation runner using the new framework.
This demonstrates the cleaner structure for evaluation execution.
"""

import sys
from evals.framework.runner import EvalRunner
from evals.framework.base_config import BaseEvalConfig


def main():
    if len(sys.argv) < 2:
        config = BaseEvalConfig()
        config._print_help()
        sys.exit(1)
    
    model_name = sys.argv[1]
    args = sys.argv[2:]  # Arguments after model name
    
    # Create configuration and runner
    config = BaseEvalConfig()
    runner = EvalRunner(config)
    
    # Run the evaluation
    runner.run(model_name, args)


if __name__ == "__main__":
    main()