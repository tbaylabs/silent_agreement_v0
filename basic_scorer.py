from inspect_ai.scorer import score_reducer, ScoreReducer, Score, value_to_float

@score_reducer(name="sum")
def sum_score() -> ScoreReducer:
    to_float = value_to_float()
    
    def reduce(scores: list[Score]) -> Score:
        """Sum up all score values."""
        values = [to_float(score.value) for score in scores]
        total = sum(values)
        return Score(value=total)
    
    return reduce
