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
import requests


class MockModel:
    def __init__(self, val: int):
        self.some_value = val

    def some_function(self, number: int):
        orig_some_val = self.some_value
        self.some_value = number
        return orig_some_val + number


class TestScientist(unittest.TestCase):
    def mockPost(self, *args, **kwargs):
        res = requests.Response()
        return res

    def setUp(self):
        self.og_put = requests.put
        self.og_post = requests.post
        requests.put = lambda _, data, **kwargs: kwargs.pop("files")
        requests.post = self.mockPost

    def tearDown(self):
        requests.put = self.og_put
        requests.post = self.og_post

    def test_package(self):
        request_dict = package(MockModel(42), "modelName")
        serialized_model = request_dict.get("pkledFile")
        model = cloudpickle.load(serialized_model)
        assert model.some_value == 42
        assert model.some_function(1) == 43
        assert model.some_value == 1
