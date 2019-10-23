"""Invalid config with wrong evaluator assignment."""
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import Pipeline

from tests.dataloaders.dummy_loader import MockTrainTestLoader
from tests.evaluators.dummy_evaluator import DummyGridEvaluator

dataloader = MockTrainTestLoader()

pipeline = Pipeline([("classifier", DummyClassifier(strategy='constant'))])

evaluator = DummyGridEvaluator
