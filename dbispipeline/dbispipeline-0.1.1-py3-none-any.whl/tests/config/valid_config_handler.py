"""Valid config using the dummy implementations."""
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import Pipeline

from tests.dataloaders.dummy_loader import MockTrainTestLoader
from tests.evaluators.dummy_evaluator import DummyGridEvaluator
from tests.result_handlers.dummy_result_handlers import dummy_result_handler

dataloader = MockTrainTestLoader()

pipeline = Pipeline([("classifier", DummyClassifier(strategy='constant'))])

evaluator = DummyGridEvaluator(
    parameters={'classifier__constant': [41, 42, 42]},
    grid_parameters={'verbose': 1})

result_handlers = [dummy_result_handler]
