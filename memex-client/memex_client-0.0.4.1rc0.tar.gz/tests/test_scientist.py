#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_brainiac
----------------------------------

tests for `brainiac` module.
"""

import unittest
import cloudpickle
from memex_client.scientist import package


class MockModel:
    def __init__(self, val: int):
        self.some_value = val

    def some_function(self, number: int):
        orig_some_val = self.some_value
        self.some_value = number
        return orig_some_val + number


class TestScientist(unittest.TestCase):
    def test_package(self):
        serialized_model = package(MockModel(42))
        model = cloudpickle.loads(serialized_model)
        assert model.some_value == 42
        assert model.some_function(1) == 43
        assert model.some_value == 1
