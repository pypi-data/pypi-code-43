import mock
import unittest
from logging import Logger

from dq import logging


class TestLogging(unittest.TestCase):

    def test_error(self):
        logger = Logger(__name__)
        logger.error = mock.MagicMock()
        data = {'a': 'b'}
        logging.error(logger, 'hi', data)
        logger.error.assert_called_with(
            'hi\n%s', '\n`a`: b', exc_info=True, extra={'data': data},
        )

    def test_error_no_payload(self):
        logger = Logger(__name__)
        logger.error = mock.MagicMock()
        logging.error(logger, 'hi')
        logger.error.assert_called_with('hi', exc_info=True)

    def test_warning(self):
        logger = Logger(__name__)
        logger.warning = mock.MagicMock()
        logging.warning(logger, 'hi', {'a': 'b'})
        logger.warning.assert_called_with(
            'hi\n%s', '\n`a`: b', exc_info=False, extra={'data': {'a': 'b'}},
        )

    def test_info(self):
        logger = Logger(__name__)
        logger.info = mock.MagicMock()
        logging.info(logger, 'hi', {'a': 'b'})
        logger.info.assert_called_with(
            'hi\n%s', '\n`a`: b', exc_info=False, extra={'data': {'a': 'b'}},
        )

    def test_debug_production(self):
        production = logging.PRODUCTION
        logging.PRODUCTION = True
        logger = Logger(__name__)
        logger.debug = mock.MagicMock()
        logging.debug(logger, 'hi', {'a': 'b'})
        logger.debug.assert_not_called()
        logging.PRODUCTION = production

    def test_debug(self):
        logger = Logger(__name__)
        logger.debug = mock.MagicMock()
        logging.debug(logger, 'hi', {'a': 'b'})
        logger.debug.assert_called_with(
            'hi\n%s', '\n`a`: b', exc_info=False, extra={'data': {'a': 'b'}},
        )
