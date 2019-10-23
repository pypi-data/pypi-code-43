"""Invalid config with wrong type of output handler."""
from dbispipeline.output_handlers import PrintHandler

from sklearn.dummy import DummyClassifier
from sklearn.pipeline import Pipeline

from tests.dataloaders.dummy_loader import MockTrainTestLoader
from tests.evaluators.dummy_evaluator import DummyGridEvaluator

dataloader = MockTrainTestLoader()

pipeline = Pipeline([("classifier", DummyClassifier(strategy='constant'))])

evaluator = DummyGridEvaluator(
    parameters={'classifier__constant': [41, 42, 42]},
    grid_parameters={'verbose': 1})

output_handlers = [PrintHandler(), MockTrainTestLoader(), PrintHandler()]
