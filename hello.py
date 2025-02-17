import os
from inspect_ai import Task, task
from inspect_ai.dataset import Sample, example_dataset
from inspect_ai.scorer import scorer, pattern, SampleScore, metric, Metric, exact
from inspect_ai.solver import generate

@metric
def match_counter() -> Metric:
    """Count matches between generated answers and targets, and print model info."""
    def metric_func(scores: list[SampleScore]):
        # model = os.getenv('INSPECT_EVAL_MODEL', 'Not set')
        # print(f"Using model: {model}")
        
        matches = sum(1 for score in scores if score.score == 1.0)
        total = len(scores)
        
        return {
            # "model": model,
            "matches": matches,
            "total": total,
            "match_rate": matches/total if total > 0 else 0
        }
    return metric_func

def create_hello_scorer():
    @scorer(metrics=[match_counter()])
    def hello_scorer(answers: list[str]):
        return exact()
    return hello_scorer

@task
def hello_world():
    return Task(
        dataset=[
            Sample(
                input="Just reply with Hello World",
                target="Hello World",
            )
        ],
        solver=[generate()],
        scorer=create_hello_scorer()(),
    )
