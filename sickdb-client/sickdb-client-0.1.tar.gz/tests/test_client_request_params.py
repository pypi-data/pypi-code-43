import os
import unittest
import json
import logging

from sickdb_client import API, ClientError


class SickdbClientTests(unittest.TestCase):

    api = API(url="http://localhost:5000", api_key="test")

    def test_request_kwargs_no_json(self):
        input = {"api_key": "dev", "foo": "bar"}
        kwargs = self.api.prepare_request_kwargs(input, json=False)
        assert kwargs["params"]["api_key"] == "dev"
        assert kwargs["params"]["foo"] == "bar"

    def test_request_kwargs_json(self):
        input = {"api_key": "dev", "foo": "bar"}
        kwargs = self.api.prepare_request_kwargs(input, json=True)
        assert kwargs["params"]["api_key"] == "dev"
        assert kwargs["json"]["foo"] == "bar"

    def test_request_kwargs_no_api_key(self):
        input = {"api_key": "dev", "foo": "bar"}
        api = API(url="http://localhost:5000")
        kwargs = api.prepare_request_kwargs(input)
        assert kwargs["params"]["api_key"] == "dev"
        assert api.api_key == "dev"

    def test_request_kwargs_file(self):
        input = {"api_key": "dev", "foo": "bar", "file": "fobj"}
        kwargs = self.api.prepare_request_kwargs(input)
        assert kwargs["files"]["file"] == "fobj"

    def test_prepare_file_create_request_kwargs(self):
        input = {"api_key": "dev", "fields": {"foo": "bar"}, "file": "fobj"}
        kwargs = self.api.files.prepare_file_create_request_kwargs(input)
        assert "data" in kwargs
        assert "fields" in kwargs["data"]

    def test_bad_request_error(self):
        api = API(url="http://foo.bar:1234/")
        try:
            api.files.get(id=1)
        except ClientError as e:
            assert True
        except Exception as e:
            print(e)
            assert False
