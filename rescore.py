import asyncio
from inspect_ai._eval import score, read_eval_log
from v0_scorer import match_valid_answers
import json
from pathlib import Path

async def rescore_log(log_path: str):
    """
    Rescore an evaluation log file using the v0 scorer.
    
    Args:
        log_path: Path to the .eval file to rescore
    """
    # Read the existing log
    eval_log = read_eval_log(
        log_path,
        header_only=False,  # We need the samples
        resolve_attachments=False,  # Don't need to resolve attachments for scoring
        format="auto"  # Let it detect based on file extension
    )
    
    # Create scorer with test_mode=True
    scorer = match_valid_answers(test_mode=True)
    
    # Score the log
    scored_log = await score(
        log=eval_log,
        scorers=scorer,
        action="overwrite"  # Replace existing scores
    )
    
    # Generate output path (original_name_rescored.eval)
    path = Path(log_path)
    output_path = path.parent / f"{path.stem}_rescored{path.suffix}"
    
    # Save the rescored log
    with open(output_path, 'w') as f:
        json.dump(scored_log.model_dump(), f, indent=2)
    
    print(f"Rescored log saved to: {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python rescore.py <path_to_eval_file>")
        sys.exit(1)
    
    log_path = sys.argv[1]
    asyncio.run(rescore_log(log_path))
