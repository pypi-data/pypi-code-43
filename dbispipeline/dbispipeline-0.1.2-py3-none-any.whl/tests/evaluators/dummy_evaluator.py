"""Dummy implementation of evaluator."""
from dbispipeline.evaluators import GridEvaluator


class DummyGridEvaluator(GridEvaluator):
    """Dummy grid evaluator."""

    def evaluate(self, model, data):
        """Evaluates to true."""
        return {'result': True}
