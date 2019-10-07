from unittest import TestCase
from swarmrob.logger import remote_logger


class TestRemoteLoggerInit(TestCase):
    def setUp(self):
        self.logger, self.broken_logger = default_setup()

    def test_init_logger(self):
        self.assertIsNotNone(self.logger.swarm_uuid)
        self.assertIsNotNone(self.logger.worker_uuid)
        self.assertIsNotNone(self.logger.remote_logger)

    def test_init_broken_logger(self):
        self.assertIsNone(self.broken_logger.swarm_uuid)
        self.assertIsNone(self.broken_logger.worker_uuid)
        self.assertIsNone(self.broken_logger.remote_logger)


class TestRemoteLoggerDebug(TestCase):
    def setUp(self):
        self.logger, self.broken_logger = default_setup()

    def test_debug(self):
        self.assertTrue(self.logger.debug("DEBUG_MESSAGE"))

    def test_debug_disabled(self):
        self.assertFalse(self.broken_logger.debug("DEBUG_MESSAGE"))


class TestRemoteLoggerError(TestCase):
    def setUp(self):
        self.logger, self.broken_logger = default_setup()

    def test_error(self):
        self.assertTrue(self.logger.error("DEBUG_MESSAGE"))

    def test_error_disabled(self):
        self.assertFalse(self.broken_logger.error("DEBUG_MESSAGE"))


class TestRemoteLoggerException(TestCase):
    def setUp(self):
        self.logger, self.broken_logger = default_setup()

    def test_exception(self):
        self.assertTrue(self.logger.error(Exception("Exception"), "DEBUG_MESSAGE"))

    def test_exception_disabled(self):
        self.assertFalse(self.broken_logger.error(Exception("Exception"), "DEBUG_MESSAGE"))


def default_setup():
    logger = remote_logger.RemoteLogger("127.0.0.1", "0", "foo", "bar")
    broken_logger = remote_logger.RemoteLogger(None, None, None, None)
    return logger, broken_logger
