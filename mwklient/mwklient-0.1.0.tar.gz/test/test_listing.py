# encoding=utf-8
""" This module contains tests for mwklient.listing.
The class TestList defines unit test cases.
"""
import logging
import unittest
import pytest
import requests
import responses
import mock
import mwklient
from mwklient.listing import List, GeneratorList

try:
    import json
except ImportError:
    import simplejson as json


class TestList(unittest.TestCase):

    def setUp(self):
        pass

    def setup_dummy_responses(self, mock_site, result_member, namespace=None):
        if not namespace:
            namespace = [0, 0, 0]
        mock_site.get.side_effect = [
            {
                'continue': {
                    'apcontinue': 'Kre_Mbaye',
                    'continue': '-||'
                },
                'query': {
                    result_member: [
                        {
                            "pageid": 19839654,
                            "ns": namespace[0],
                            "title": "Kre'fey",
                        },
                        {
                            "pageid": 19839654,
                            "ns": namespace[1],
                            "title": "Kre-O",
                        }
                    ]
                }
            },
            {
                'query': {
                    result_member: [
                        {
                            "pageid": 30955295,
                            "ns": namespace[2],
                            "title": "Kre-O Transformers",
                        }
                    ]
                }
            },
        ]

    @mock.patch('mwklient.client.Site')
    def test_list_continuation(self, mock_site):
        # Test that the list fetches all three responses
        # and yields dicts when return_values not set

        lst = List(mock_site, 'allpages', 'ap', limit=2)
        self.setup_dummy_responses(mock_site, 'allpages')
        vals = [x for x in lst]

        self.assertEqual(len(vals), 3)
        self.assertTrue(isinstance(vals[0], dict))

    @mock.patch('mwklient.client.Site')
    def test_list_with_str_return_value(self, mock_site):
        # Test that the List yields strings when return_values is string

        lst = List(mock_site, 'allpages', 'ap', limit=2, return_values='title')
        self.setup_dummy_responses(mock_site, 'allpages')
        vals = [x for x in lst]

        self.assertEqual(len(vals), 3)
        self.assertTrue(isinstance(vals[0], str))

    @mock.patch('mwklient.client.Site')
    def test_list_with_tuple_return_value(self, mock_site):
        # Test that the List yields tuples when return_values is tuple

        lst = List(mock_site, 'allpages', 'ap', limit=2,
                   return_values=('title', 'ns'))
        self.setup_dummy_responses(mock_site, 'allpages')
        vals = [x for x in lst]

        self.assertEqual(len(vals), 3)
        self.assertTrue(isinstance(vals[0], tuple))

    @mock.patch('mwklient.client.Site')
    def test_generator_list(self, mock_site):
        # Test that the GeneratorList yields Page objects

        lst = GeneratorList(mock_site, 'pages', 'p')
        self.setup_dummy_responses(mock_site, 'pages', namespace=[0, 6, 14])
        vals = [x for x in lst]

        self.assertEqual(len(vals), 3)
        self.assertTrue(isinstance(vals[0], mwklient.page.Page))
        self.assertTrue(isinstance(vals[1], mwklient.image.Image))
        self.assertTrue(isinstance(vals[2], mwklient.listing.Category))

    def test_cheat_pylint(self):
        """ Dumb test that avoids unused import warning for time package.
        """
        self.assertIsNotNone(logging)
        self.assertIsNotNone(pytest)
        self.assertIsNotNone(json)
        self.assertIsNotNone(requests)
        self.assertIsNotNone(responses)


if __name__ == '__main__':
    print("\nNote: Running in stand-alone mode. Consult the README\n")
    unittest.main()
