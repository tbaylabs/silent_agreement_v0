import os
from inspect_ai import Task, task
from inspect_ai.dataset import Sample, example_dataset
from inspect_ai.scorer import scorer, pattern, SampleScore, metric, Metric, exact
from inspect_ai.solver import generate

@metric
def model_printer() -> Metric:
    """Custom metric that prints the model name for each sample."""
    def metric_func(scores: list[SampleScore]):
        model = os.getenv('INSPECT_EVAL_MODEL', 'Not set')
        print(f"Inside scorer - INSPECT_EVAL_MODEL: {model}")
        return {"model": model}
    return metric_func

def create_hello_scorer():
    @scorer(metrics=[model_printer()])
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
