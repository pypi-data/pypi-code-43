"""Invalid config with missing pipeline."""
from tests.dataloaders.dummy_loader import MockTrainTestLoader
from tests.evaluators.dummy_evaluator import DummyGridEvaluator

dataloader = MockTrainTestLoader()

evaluator = DummyGridEvaluator(
    parameters={'classifier__constant': [41, 42, 42]},
    grid_parameters={'verbose': 1})
