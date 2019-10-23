"""Invalid config with missing evaluator."""
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import Pipeline

from tests.dataloaders.dummy_loader import MockTrainTestLoader

dataloader = MockTrainTestLoader()

pipeline = Pipeline([("classifier", DummyClassifier(strategy='constant'))])
