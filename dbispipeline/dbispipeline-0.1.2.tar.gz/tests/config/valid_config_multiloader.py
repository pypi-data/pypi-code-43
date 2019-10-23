"""Tests a dataloader with multiple runs"""
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import make_pipeline

from tests.dataloaders.dummy_loader import MockMultiLoader
from tests.evaluators.dummy_evaluator import DummyGridEvaluator

dataloader = MockMultiLoader(5)

pipeline = make_pipeline(DummyClassifier(strategy='constant'))

evaluator = DummyGridEvaluator(
    parameters={'classifier__constant': [41, 42, 42]},
    grid_parameters={'verbose': 1})
