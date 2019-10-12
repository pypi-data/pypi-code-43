# encoding=utf-8
""" This module contains tests for mwklient.page.
The class TestPage defines unit test cases.
"""
import logging
import unittest
import pytest
import requests
import responses
import mock
import mwklient
from mwklient.page import Page
from mwklient.client import Site
from mwklient.listing import Category
from mwklient.errors import APIError, AssertUserFailedError, ProtectedPageError, InvalidPageTitle

try:
    import json
except ImportError:
    import simplejson as json


class TestPage(unittest.TestCase):

    def setUp(self):
        pass

    @mock.patch('mwklient.client.Site')
    def test_api_call_on_page_init(self, mock_site):
        # Check that site.get() is called once on Page init

        title = 'Some page'
        mock_site.get.return_value = {
            'query': {'pages': {'1': {}}}
        }
        Page(mock_site, title)

        # test that Page called site.get with the right parameters
        mock_site.get.assert_called_once_with(
            'query', inprop='protection', titles=title, prop='info')

    @mock.patch('mwklient.client.Site')
    def test_nonexisting_page(self, mock_site):
        # Check that API response results in page.exists being set to False

        title = 'Some nonexisting page'
        mock_site.get.return_value = {
            'query': {'pages': {'-1': {'missing': ''}}}
        }
        page = Page(mock_site, title)

        self.assertFalse(page.exists)

    @mock.patch('mwklient.client.Site')
    def test_existing_page(self, mock_site):
        # Check that API response results in page.exists being set to True

        title = 'Norge'
        mock_site.get.return_value = {
            'query': {'pages': {'728': {}}}
        }
        page = Page(mock_site, title)

        self.assertTrue(page.exists)

    @mock.patch('mwklient.client.Site')
    def test_invalid_title(self, mock_site):
        # Check that API page.exists is False for invalid title

        title = '[Test]'
        reason = "The requested page title contains invalid characters: \"[\"."
        mock_site.get.return_value = {
            "query": {
                "pages": {
                    "-1": {
                        "title": "[Test]",
                        "invalidreason": reason,
                        "invalid": ""
                    }
                }
            }
        }
        with pytest.raises(InvalidPageTitle):
            Page(mock_site, title)

    @mock.patch('mwklient.client.Site')
    def test_pageprops(self, mock_site):
        # Check that variouse page props are read correctly from API response

        title = 'Some page'
        mock_site.get.return_value = {
            'query': {
                'pages': {
                    '728': {
                        'contentmodel': 'wikitext',
                        'counter': '',
                        'lastrevid': 13355471,
                        'length': 58487,
                        'ns': 0,
                        'pageid': 728,
                        'pagelanguage': 'nb',
                        'protection': [],
                        'title': title,
                        'touched': '2014-09-14T21:11:52Z'
                    }
                }
            }
        }
        page = Page(mock_site, title)

        self.assertTrue(page.exists)
        self.assertFalse(page.redirect)
        self.assertEqual(page.revision, 13355471)
        self.assertEqual(page.length, 58487)
        self.assertEqual(page.namespace, 0)
        self.assertEqual(page.name, title)
        self.assertEqual(page.page_title, title)

    @mock.patch('mwklient.client.Site')
    def test_protection_levels(self, mock_site):
        # If page is protected, check that protection is parsed correctly

        title = 'Some page'
        mock_site.get.return_value = {
            'query': {
                'pages': {
                    '728': {
                        'protection': [
                            {
                                'expiry': 'infinity',
                                'level': 'autoconfirmed',
                                'type': 'edit'
                            },
                            {
                                'expiry': 'infinity',
                                'level': 'sysop',
                                'type': 'move'
                            }
                        ]
                    }
                }
            }
        }
        mock_site.rights = ['read', 'edit', 'move']

        page = Page(mock_site, title)

        self.assertEqual(page.protection, {
            'edit': ('autoconfirmed', 'infinity'),
            'move': ('sysop', 'infinity')})
        self.assertTrue(page.can('read'))
        # User does not have 'autoconfirmed' right
        self.assertFalse(page.can('edit'))
        self.assertFalse(page.can('move'))  # User does not have 'sysop' right

        mock_site.rights = ['read', 'edit', 'move', 'autoconfirmed']

        self.assertTrue(page.can('edit'))   # User has 'autoconfirmed'  right
        self.assertFalse(page.can('move'))  # User doesn't have 'sysop'  right

        mock_site.rights = ['read', 'edit', 'move',
                            'autoconfirmed', 'editprotected']

        self.assertTrue(page.can('edit'))  # User has 'autoconfirmed'  right
        self.assertTrue(page.can('move'))  # User has 'sysop' right

    @mock.patch('mwklient.client.Site')
    def test_redirect(self, mock_site):
        # Check that page.redirect is set correctly

        title = 'Some redirect page'
        mock_site.get.return_value = {
            "query": {
                "pages": {
                    "796917": {
                        "contentmodel": "wikitext",
                        "counter": "",
                        "lastrevid": 9342494,
                        "length": 70,
                        "ns": 0,
                        "pageid": 796917,
                        "pagelanguage": "nb",
                        "protection": [],
                        "redirect": "",
                        "title": title,
                        "touched": "2014-08-29T22:25:15Z"
                    }
                }
            }
        }
        page = Page(mock_site, title)

        self.assertTrue(page.exists)
        self.assertTrue(page.redirect)

    @mock.patch('mwklient.client.Site')
    def test_captcha(self, mock_site):
        # Check that Captcha results in EditError
        mock_site.blocked = False
        mock_site.rights = ['read', 'edit']

        title = 'Norge'
        mock_site.get.return_value = {
            'query': {'pages': {'728': {'protection': []}}}
        }
        page = Page(mock_site, title)
        mock_site.post.return_value = {
            'edit': {'result': 'Failure', 'captcha': {
                'type': 'math',
                'mime': 'text/tex',
                'id': '509895952',
                'question': '36 + 4 = '
            }}
        }

        # For now, mwklient will just raise an EditError.
        # <https://github.com/mwklient/mwklient/issues/33>
        with pytest.raises(mwklient.errors.EditError):
            page.edit('Some text')


class TestPageApiArgs(unittest.TestCase):

    def setUp(self):
        title = 'Some page'
        self.page_text = 'Hello world'

        mock_site = mock.patch('mwklient.client.Site').start()
        self.site = mock_site()

        self.site.get.return_value = {
            'query': {'pages': {'1': {'title': title}}}}
        self.site.rights = ['read']
        self.site.api_limit = 500
        self.site.version = (1, 32, 0)

        self.page = Page(self.site, title)

        revisions = [{'*': 'Hello world', 'timestamp': '2014-08-29T22:25:15Z'}]
        self.site.get.return_value = {'query': {'pages': {'2': {
            'ns': 0, 'pageid': 2, 'revisions': revisions, 'title': title
        }}}}

    def get_last_api_call_args(self, http_method='POST'):
        if http_method == 'GET':
            args, kwargs = self.site.get.call_args
        else:
            args, kwargs = self.site.post.call_args
        # action = args[0]
        args = args[1:]
        kwargs.update(args)
        return kwargs

    def tearDown(self):
        mock.patch.stopall()

    def test_get_page_text(self):
        # Check that page.text() works, and that a correct API call is made
        text = self.page.text()
        args = self.get_last_api_call_args(http_method='GET')

        self.assertEqual(text, self.page_text)
        self.assertEqual(args, {
            'prop': 'revisions',
            'rvdir': 'older',
            'titles': self.page.page_title,
            'uselang': None,
            'rvprop': 'content|timestamp',
            'rvlimit': '1',
            'rvslots': 'main',
        })

    def test_get_page_text_cached(self):
        # Check page.text() caching
        self.page.revisions = mock.Mock(return_value=iter([]))
        self.page.text()
        self.page.text()
        # When cache is hit, revisions is not, so call_count should be 1
        assert self.page.revisions.call_count == 1
        self.page.text(cache=False)
        # With cache explicitly disabled, we should hit revisions
        assert self.page.revisions.call_count == 2

    def test_get_section_text(self):
        # Check that the 'rvsection' parameter is sent to the API
        self.page.text(section=0)
        args = self.get_last_api_call_args(http_method='GET')

        assert args['rvsection'] == '0'

    def test_get_text_expanded(self):
        # Check that the 'rvexpandtemplates' parameter is sent to the API
        self.page.text(expandtemplates=True)
        args = self.get_last_api_call_args(http_method='GET')

        assert self.site.expandtemplates.call_count == 1
        assert args.get('rvexpandtemplates') is None

    def test_assertuser_true(self):
        # Check that assert=user is sent when force_login=True
        self.site.blocked = False
        self.site.rights = ['read', 'edit']
        self.site.logged_in = True
        self.site.force_login = True

        self.site.api.return_value = {
            'edit': {'result': 'Ok'}
        }
        self.page.edit('Some text')
        args = self.get_last_api_call_args()

        assert args['assert'] == 'user'

    def test_assertuser_false(self):
        # Check that assert=user is not sent when force_login=False
        self.site.blocked = False
        self.site.rights = ['read', 'edit']
        self.site.logged_in = False
        self.site.force_login = False

        self.site.api.return_value = {
            'edit': {'result': 'Ok'}
        }
        self.page.edit('Some text')
        args = self.get_last_api_call_args()

        assert 'assert' not in args

    def test_handle_edit_error_assertuserfailed(self):
        # Check that AssertUserFailedError is triggered
        api_error = APIError('assertuserfailed',
                             'Assertion that the user is logged in failed',
                             'See https://en.wikipedia.org/w/api.php for API usage')

        with pytest.raises(AssertUserFailedError):
            self.page.handle_edit_error(api_error, 'n/a')

    def test_handle_edit_error_protected(self):
        # Check that ProtectedPageError is triggered
        api_error = APIError('protectedpage',
                             'The "editprotected" right is required to edit this page',
                             'See https://en.wikipedia.org/w/api.php for API usage')

        with pytest.raises(ProtectedPageError) as pp_error:
            self.page.handle_edit_error(api_error, 'n/a')

        self.assertEqual(pp_error.value.code, 'protectedpage')
        error_value = 'The "editprotected" right is required to edit this page'
        self.assertEqual(str(pp_error.value), error_value)

    def test_get_page_categories(self):
        """Check that page.categories() works and that a correct API call is
        made
        """

        self.site.get.return_value = {
            "batchcomplete": "",
            "query": {
                "pages": {
                    "1009371": {
                        "pageid": 1009371,
                        "ns": 14,
                        "title": "Category:1879 births",
                    },
                    "1005547": {
                        "pageid": 1005547,
                        "ns": 14,
                        "title": "Category:1955 deaths",
                    }
                }
            }
        }

        cats = list(self.page.categories())
        args = self.get_last_api_call_args(http_method='GET')

        iiprop = 'timestamp|user|comment|url|size|sha1|metadata|archivename'
        dic = {
            'generator': 'categories',
            'titles': self.page.page_title,
            'iiprop': iiprop,
            'inprop': 'protection',
            'prop': 'info|imageinfo',
            'gcllimit': repr(self.page.site.api_limit),
        }
        self.assertEqual(dic, args)

        self.assertEqual({c.name for c in cats}, set([
            'Category:1879 births',
            'Category:1955 deaths',
        ]))

    def test_cheat_pylint(self):
        """ Dumb test that avoids unused import warning for time package.
        """
        self.assertIsNotNone(json)
        self.assertIsNotNone(logging)
        self.assertIsNotNone(Category)
        self.assertIsNotNone(requests)
        self.assertIsNotNone(responses)
        self.assertIsNotNone(Site)


if __name__ == '__main__':
    unittest.main()
