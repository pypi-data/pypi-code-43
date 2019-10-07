from unittest import TestCase
from swarmrob.logger import local_logger


class TestLocalLoggerLogMethodCall(TestCase):
    def setUp(self):
        self.logger = local_logger.LocalLogger()

    def test_log_method_call(self):
        self.logger.log_calls = True
        self.logger.enable = True
        self.assertTrue(self.logger.log_method_call("CLASS_NAME", "METHOD_NAME"))

    def test_log_method_call_calls_disabled(self):
        self.logger.log_calls = False
        self.logger.enable = True
        self.assertFalse(self.logger.log_method_call("CLASS_NAME", "METHOD_NAME"))

    def test_log_method_call_logger_disabled(self):
        self.logger.log_calls = True
        self.logger.enable = False
        self.assertFalse(self.logger.log_method_call("CLASS_NAME", "METHOD_NAME"))

    def test_log_method_call_both_disabled(self):
        self.logger.log_calls = False
        self.logger.enable = False
        self.assertFalse(self.logger.log_method_call("CLASS_NAME", "METHOD_NAME"))


class TestLocalLoggerLogFunctionCall(TestCase):
    def setUp(self):
        self.logger = local_logger.LocalLogger()

    def test_log_function_call(self):
        self.logger.log_calls = True
        self.logger.enable = True
        self.assertTrue(self.logger.log_call("FUNCTION_NAME"))

    def test_log_function_call_calls_disabled(self):
        self.logger.log_calls = False
        self.logger.enable = True
        self.assertFalse(self.logger.log_call("FUNCTION_NAME"))

    def test_log_function_call_logger_disabled(self):
        self.logger.log_calls = True
        self.logger.enable = False
        self.assertFalse(self.logger.log_call("FUNCTION_NAME"))

    def test_log_function_call_both_disabled(self):
        self.logger.log_calls = False
        self.logger.enable = False
        self.assertFalse(self.logger.log_call("FUNCTION_NAME"))


class TestLocalLoggerDebug(TestCase):
    def setUp(self):
        self.logger = local_logger.LocalLogger()

    def test_debug(self):
        self.logger.enable = True
        self.assertTrue(self.logger.debug("DEBUG_MESSAGE"))

    def test_debug_disabled(self):
        self.logger.enable = False
        self.assertFalse(self.logger.debug("DEBUG_MESSAGE"))


class TestLocalLoggerError(TestCase):
    def setUp(self):
        self.logger = local_logger.LocalLogger()

    def test_error(self):
        self.logger.enable = True
        self.assertTrue(self.logger.error("DEBUG_MESSAGE"))

    def test_error_disabled(self):
        self.logger.enable = False
        self.assertFalse(self.logger.error("DEBUG_MESSAGE"))


class TestLocalLoggerException(TestCase):
    def setUp(self):
        self.logger = local_logger.LocalLogger()

    def test_exception(self):
        self.logger.enable = True
        self.assertTrue(self.logger.error(Exception("Exception"), "DEBUG_MESSAGE"))

    def test_exception_disabled(self):
        self.logger.enable = False
        self.assertFalse(self.logger.error(Exception("Exception"), "DEBUG_MESSAGE"))
