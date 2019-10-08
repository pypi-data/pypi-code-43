import unittest

from behave.model import Table

from rikki.behave.context import Context
from rikki.behave.steps.utils import create_pattern, http_data


class TestUtils(unittest.TestCase):

    def test_should_create_simplified_pattern(self):
        pattern = create_pattern("*google*")

        self.assertNotEqual(pattern.fullmatch("www.google.com"), None,
                            "Simplified Wildcard pattern doesn't match value")

        pattern = create_pattern("*google.com")

        self.assertNotEqual(pattern.fullmatch("www.google.com"), None,
                            "Simplified Wildcard pattern doesn't match value")

        pattern = create_pattern("google.com")

        self.assertEqual(pattern.fullmatch("www.google.com"), None,
                         "Simplified Wildcard pattern match value, but shouldn't")

        pattern = create_pattern("127.0.0.1")

        self.assertNotEqual(pattern.fullmatch("127.0.0.1"), None,
                            "Simplified Wildcard pattern doesn't match value")

        self.assertEqual(pattern.fullmatch("127.0.0.1:8080"), None,
                         "Simplified Wildcard pattern match value, but shouldn't")

        pattern = create_pattern("*127.0.0.1*")

        self.assertEqual(pattern.fullmatch("127x0x0x1"), None,
                         "Simplified Wildcard pattern match value, but shouldn't")

    def test_should_create_full_featured_pattern(self):
        pattern = create_pattern("r\".*127.0.0.1.*\"")

        self.assertNotEqual(pattern.fullmatch("127.0.0.1"), None,
                            "Simplified Wildcard pattern doesn't match value")

        self.assertNotEqual(pattern.fullmatch("127x0x0x1"), None,
                            "Simplified Wildcard pattern doesn't match value")
        self.assertEqual(pattern.fullmatch("127..0.0.1"), None,
                         "Simplified Wildcard pattern match value, but shouldn't")

        pattern = create_pattern("r\".*127\.0\.0\.1\.*\"")

        self.assertNotEqual(pattern.fullmatch("127.0.0.1"), None,
                            "Simplified Wildcard pattern doesn't match value")

        self.assertEqual(pattern.fullmatch("127x0x0x1"), None,
                         "Simplified Wildcard pattern match value, but shouldn't")
        self.assertEqual(pattern.fullmatch("127..0.0.1"), None,
                         "Simplified Wildcard pattern match value, but shouldn't")

    def test_should_parse_http_data(self):
        table = Table(headings=["option", "value"])
        table.add_row(["port", "8080"])
        table.add_row(["host", "localhost"])
        table.add_row(["method", "GET"])
        table.add_row(["path", "/path/to/"])
        table.add_row(["headers", "{\"header1\": \"1\"}"])
        table.add_row(["params", "{\"param1\": \"1\"}"])
        table.add_row(["content", "content"])
        table.add_row(["response_code", "200"])
        table.add_row(["response_headers", "{\"response_header1\": \"1\"}"])
        table.add_row(["response_content", "response content"])
        table.add_row(["replace_port", "8181"])
        table.add_row(["replace_host", "127.0.0.1"])
        table.add_row(["replace_path", "/to/path/"])
        table.add_row(["replace_headers", "{\"replace_header1\": \"1\"}"])
        table.add_row(["replace_params", "{\"replace_param1\": \"1\"}"])
        table.add_row(["replace_content", "replace content"])
        table.add_row(["replace_response_code", "201"])
        table.add_row(["replace_response_content", "replace response content"])
        table.add_row(["replace_response_headers", "{\"replace_response_header1\": \"1\"}"])

        context = Context(table=table)

        result = http_data(context)

        self.assertEqual(result.filter_request.port, "8080")
        self.assertEqual(result.filter_request.method, "GET")
        self.assertEqual(result.filter_request.host, "localhost")
        self.assertEqual(result.filter_request.path, "/path/to/")
        self.assertEqual(result.filter_request.headers, {"header1": "1"})
        self.assertEqual(result.filter_request.params, {"param1": "1"})
        self.assertEqual(result.filter_request.content, "content")

        self.assertEqual(result.filter_response.code, 200)
        self.assertEqual(result.filter_response.headers, {"response_header1": "1"})
        self.assertEqual(result.filter_response.content, "response content")

        self.assertEqual(result.replacement_request.port, "8181")
        self.assertEqual(result.replacement_request.host, "127.0.0.1")
        self.assertEqual(result.replacement_request.path, "/to/path/")
        self.assertEqual(result.replacement_request.headers, {"replace_header1": "1"})
        self.assertEqual(result.replacement_request.params, {"replace_param1": "1"})
        self.assertEqual(result.replacement_request.content, "replace content")

        self.assertEqual(result.replacement_response.code, 201)
        self.assertEqual(result.replacement_response.headers, {"replace_response_header1": "1"})
        self.assertEqual(result.replacement_response.content, "replace response content")
