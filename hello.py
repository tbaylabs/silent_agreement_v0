import os
from inspect_ai import Task, task
from inspect_ai.dataset import Sample, example_dataset
from inspect_ai.scorer import exact
from inspect_ai.solver import generate

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
        scorer=exact(),
    )

# Print the model being used for evaluation
print(f"INSPECT_EVAL_MODEL: {os.getenv('INSPECT_EVAL_MODEL', 'Not set')}")
# print(example_dataset())
