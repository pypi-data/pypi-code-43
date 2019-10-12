"""Tests the Scraper class in KomiDL"""

import os
import sys
import unittest
from unittest import mock

from multiprocessing.dummy import Lock
sys.path.append(os.path.abspath('..'))

from komidl.scraper import Scraper
from komidl.exceptions import ExtractorFailed, InvalidURL


class ScraperTest(unittest.TestCase):
    """Tests the Scraper class in KomiDL"""
    def setUp(self):
        """Create the Scraper object for usage"""
        self.scraper = Scraper(3)

    ####################################################################### 
    # Miscellaneous
    #######################################################################

    def test_change_extension(self):
        """Test the function that changes file ext for a URL"""
        url = "http://website.com/test/image.jpg"
        ext = "png"
        expected = "http://website.com/test/image.png"
        actual = self.scraper._change_extension(url, ext)
        self.assertEqual(actual, expected)

    def test_get_extension(self):
        test_cases = (
                      # Test 'best-case' scenario
                      ('img.jpg', ('img', 'jpg')),
                      # Test image with '.' in middle
                      ('thing.img.gif', ('thing.img', 'gif')),
                     )
        for img, (expected_path, expected_ext) in test_cases:
            (actual_path, actual_ext) = self.scraper._get_extension(img)
            self.assertEqual(actual_path, expected_path)
            self.assertEqual(actual_ext, expected_ext)

    def test_build_title(self):
        test_cases = (
                      (# Test a 'best-case' scenario
                       '[DNSHENG][EN] Some Title',
                       {
                        'Title': 'Some Title',
                        'Languages': 'English',
                        'Authors': 'DNSheng'
                       }
                      ),
                      (# Test no title and multiple languages
                       '[PICASSO][IT] UNTITLED',
                       {
                        'Languages': ['Italian', 'English'],
                        'Artists': 'Picasso'
                       }
                      ),
                      (# Test no credit and chapters
                       '[UNKNOWN][JA][0001-0004] Cool stories',
                       {
                        'Title': 'Cool stories',
                        'Languages': ['Japanese', 'English'],
                        'Chapters': '0001-0004',
                       }
                      ),
                      (# Test group credit
                       '[MINUTEMEN][JA] A settlement needs your help',
                       {
                        'Title': 'A settlement needs your help',
                        'Languages': ['Japanese', 'English'],
                        'Groups': 'Minutemen'
                       }
                      ),
                      (# Test multiple credits
                       '[BOB ROSSxPICASSO][JA] Picture gallery',
                       {
                        'Title': 'Picture gallery',
                        'Languages': ['Japanese', 'English'],
                        'Artists': ['Bob Ross', 'Picasso']
                       }
                      ),

                      (# Test credit priority
                       '[SHAKESPEARE][EN] Romeo & Juliet',
                       {
                        'Title': 'Romeo & Juliet',
                        'Languages': 'English',
                        'Authors': 'Shakespeare',
                        'Artists': 'Bob Ross',
                        'Groups': 'Dead Poets Society',
                       }
                      ),
                     )
        for expected, tag_dict in test_cases:
            actual = self.scraper._build_title(tag_dict)
            self.assertEqual(actual, expected)

    ####################################################################### 
    # _download_image()
    #######################################################################
    #def test_download_image(self):
    #    test_cases = (
    #                  (# Test a valid image URL
    #                   '001.png',
    #                   'http://gallery.com/g/abc/001.png',
    #                   '001.png'
    #                  ),
    #                  (# Test a URL that needs to be re-tried
    #                   '001.jpg',
    #                   'http://gallery.com/g/abc/001.jpg',
    #                   '001.png'
    #                  ),
    #                 )

    #    # Set up the mock functions
    #    def mock_retry_request(*args, **kwargs):
    #        # Mock the session.get, only an 'png' img  without 'exception'
    #        # in the URL will return 200
    #        class MockResponse:
    #            def __init__(self, status_code):
    #                self.status_code = status_code
    #        ext = args[0].split('.')[-1]
    #        if ext == 'png':
    #            return MockResponse(200)
    #        return MockResponse(404)

    #    def mock_fix_extension(filename):
    #        path = '.'.join(filename.split('.')[:-1])
    #        return f"{path}.png"

    #    mock_do_nothing = mock.Mock(return_value=None)

    #    self.scraper._session.get = mock_retry_request
    #    self.scraper._write_image = mock_do_nothing
    #    self.scraper._retry_download_image = mock_do_nothing
    #    self.scraper._update_status = mock_do_nothing
    #    self.scraper._fix_extension = mock_fix_extension

    #    for path, url, expected in test_cases:
    #        actual = self.scraper._download_image(path, url)
    #        self.assertEqual(actual, expected)

    #def test_download_image_exception(self):
    #    test_cases = (
    #                  (# Test an image URL returning 429
    #                   '001.png',
    #                   'http://gallery.com/g/abc/001.png',
    #                   ExtractorFailed
    #                  ),
    #                  (# Test an image URL returning 429
    #                   '001.png',
    #                   'http://exception.com/g/abc/001.png',
    #                   InvalidURL
    #                  ),
    #                 )

    #    # Set up the mock functions
    #    def mock_retry_request(*args, **kwargs):
    #        # Returns a mock 429 response for all URLs
    #        # Returns a mock 404 response otherwise
    #        class MockResponse:
    #            def __init__(self, status_code):
    #                self.status_code = status_code
    #        if 'exception' in args[0]:
    #            return MockResponse(429)
    #        return MockResponse(404)

    #    self.scraper._session.get = mock_retry_request

    #    for path, url, expected in test_cases:
    #        self.assertRaises(expected,
    #                          self.scraper._download_image,
    #                          path,
    #                          url)

    ######################################################################## 
    ## _retry_download_image()
    ########################################################################
    #def test_retry_download_image(self):
    #    test_cases = (
    #                  (# Test retrying until an 'svg' image is found
    #                   '001.jpg',
    #                   'http://gallery.com/g/abc/001.jpg',
    #                   None
    #                  ),
    #                 )

    #    # Set up the mock functions
    #    def mock_retry_request(*args, **kwargs):
    #        # Mock the session.get, only an 'svg' img will return 200
    #        class MockResponse:
    #            def __init__(self, status_code):
    #                self.status_code = status_code
    #        ext = args[0].split('.')[-1]
    #        if ext == 'svg':
    #            return MockResponse(200)
    #        return MockResponse(404)

    #    self.scraper._session.get = mock_retry_request
    #    self.scraper._write_image = mock.Mock(return_value=None)

    #    for path, url, expected in test_cases:
    #        actual = self.scraper._retry_download_image(path, url)
    #        self.assertEqual(actual, expected)

    #def test_retry_download_image_exception(self):
    #    test_cases = (
    #                  (# Test exhaustive retries with an unsupported img format
    #                   '001.test',
    #                   'http://gallery.com/g/abc/001.test',
    #                   ExtractorFailed
    #                  ),
    #                 )

    #    # Set up the mock functions
    #    def mock_retry_request(*args, **kwargs):
    #        # Mock the requests.get, only a 'png' img will return 200
    #        class MockResponse:
    #            def __init__(self, status_code):
    #                self.status_code = status_code
    #        return MockResponse(404)

    #    self.scraper._session.get = mock_retry_request
    #    self.scraper._write_image = mock.Mock(return_value=None)

    #    for path, url, expected in test_cases:
    #        self.assertRaises(ExtractorFailed,
    #                          self.scraper._retry_download_image,
    #                          path,
    #                          url)
