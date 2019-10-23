# noqa: D100
import unittest
from collections import Iterable

import dbispipeline.core as core
from dbispipeline.base import Loader
from dbispipeline.evaluators import Evaluator
from dbispipeline.output_handlers import OutputHandler

from sklearn.base import BaseEstimator


class TestCore(unittest.TestCase):
    """Tests for the dbispipeline core class."""

    def test_load_config(self):
        """Tests if load config loads a valid config correctly."""
        config = core.load_config('tests/config/valid_config.py')

        self.assertTrue(isinstance(config.dataloader, Loader))
        self.assertTrue(isinstance(config.pipeline, BaseEstimator))
        self.assertTrue(isinstance(config.evaluator, Evaluator))
        self.assertTrue(isinstance(config.output_handlers, Iterable))

        for handler in config.output_handlers:
            self.assertTrue(isinstance(handler, OutputHandler))

    def test_load_config_invalid(self):
        """Tests if load config detects invalid configs."""
        configs = [
            'tests/config/invalid_dataloader_1.py',
            'tests/config/invalid_dataloader_2.py',
            'tests/config/invalid_pipeline.py',
            'tests/config/invalid_evaluator_1.py',
            'tests/config/invalid_evaluator_2.py',
            'tests/config/invalid_output_handler_1.py',
            'tests/config/invalid_output_handler_2.py',
        ]

        for config in configs:
            self.assertRaises(ValueError, core.load_config, config)

    def test_run(self):
        """Tests if run can execute a valid pipeline."""
        pipeline = core.Core('tests/config/valid_config.py')
        pipeline.run()
        self.assertTrue(True)

    def test_run_handler(self):
        """Tests if run can execute a valid pipeline with a handler."""
        pipeline = core.Core('tests/config/valid_config_handler.py')
        pipeline.run()
        self.assertTrue(True)

    def test_run_multi(self):
        """Tests a configuration with a multi loader"""
        pipeline = core.Core('tests/config/valid_config_multiloader.py')
        pipeline.run()
        self.assertTrue(True)
