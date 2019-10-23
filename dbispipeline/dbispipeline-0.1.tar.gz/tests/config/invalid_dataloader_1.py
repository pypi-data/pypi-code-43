"""Invalid config with no dataloader."""
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import Pipeline

from tests.evaluators.dummy_evaluator import DummyGridEvaluator

pipeline = Pipeline([("classifier", DummyClassifier(strategy='constant'))])

evaluator = DummyGridEvaluator(
    parameters={'classifier__constant': [41, 42, 42]},
    grid_parameters={'verbose': 1})
