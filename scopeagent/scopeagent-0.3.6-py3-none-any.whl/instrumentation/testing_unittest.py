import inspect
import logging
import traceback

import six
import wrapt

from . import run_once
from ..tracer import tags
from ..tracer.exception import get_exception_log_fields

logger = logging.getLogger(__name__)


class TestResultProxy(wrapt.ObjectProxy):
    def __init__(self, wrapped, span):
        super(TestResultProxy, self).__init__(wrapped)
        self._span = span

    def addError(self, test, err):
        etype, value, tb = err
        self._span.set_tag(tags.TEST_STATUS, tags.TEST_STATUS_ERROR)
        self._span.set_tag(tags.ERROR, True)
        kv = {
            tags.EVENT: 'error',
            tags.MESSAGE: ''.join(traceback.format_exception_only(etype, value)).strip(),
        }
        kv.update(get_exception_log_fields(etype, value, tb))
        self._span.log_kv(kv)
        return self.__wrapped__.addError(test, err)

    def addFailure(self, test, err):
        etype, value, tb = err
        self._span.set_tag(tags.TEST_STATUS, tags.TEST_STATUS_FAIL)
        self._span.set_tag(tags.ERROR, True)
        kv = {
            tags.EVENT: 'test_failure',
            tags.MESSAGE: 'Test failed',
        }
        kv.update(get_exception_log_fields(etype, value, tb))
        self._span.log_kv(kv)
        return self.__wrapped__.addFailure(test, err)

    def addSuccess(self, test):
        self._span.set_tag(tags.TEST_STATUS, tags.TEST_STATUS_PASS)
        return self.__wrapped__.addSuccess(test)

    def addSkip(self, test, reason):
        self._span.set_tag(tags.TEST_STATUS, tags.TEST_STATUS_SKIP)
        self._span.log_kv({
            tags.EVENT: 'test_skip',
            tags.MESSAGE: reason,
        })
        return self.__wrapped__.addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        etype, value, tb = err
        self._span.set_tag(tags.TEST_STATUS, tags.TEST_STATUS_PASS)
        kv = {
            tags.EVENT: 'expected_failure',
            tags.MESSAGE: 'Test failed as expected',
        }
        kv.update(get_exception_log_fields(etype, value, tb))
        self._span.log_kv(kv)
        return self.__wrapped__.addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test):
        self._span.set_tag(tags.TEST_STATUS, tags.TEST_STATUS_FAIL)
        self._span.set_tag(tags.ERROR, True)
        self._span.log_kv({
            tags.EVENT: 'unexpected_success',
            tags.MESSAGE: 'Test passed unexpectedly',
        })
        return self.__wrapped__.addUnexpectedSuccess(test)


@run_once
def patch(tracer):
    def wrapper(wrapped, instance, args, kwargs):
        logger.debug("intercepting test: instance=%s args=%s kwargs=%s", instance, args, kwargs)
        # result argument to UnitTest.run() is optional. If not given, default is created.
        if args:
            result = args[0]
        elif 'result' in kwargs:
            result = kwargs['result']
        else:
            result = instance.defaultTestResult()

        try:
            test_method = getattr(instance, instance._testMethodName)
            # If a test is skipped by unittest.skip, it will be wrapped (due to functools.update_wrapper).
            # Not available on Python 2.7.
            if hasattr(test_method, '__wrapped__'):
                test_method = test_method.__wrapped__
            file = inspect.getsourcefile(test_method)
            lines, first_line = inspect.getsourcelines(test_method)
            code = "%s:%d:%d" % (file, first_line, first_line + len(lines) - 1)
        except (IOError, OSError,):
            code = ""

        if six.PY2:
            name = instance.__class__.__name__
        else:
            name = instance.__class__.__qualname__
        with tracer.start_active_span(
                operation_name=instance._testMethodName,
                tags={
                    tags.SPAN_KIND: tags.TEST,
                    tags.TEST_FRAMEWORK: 'unittest',
                    tags.TEST_SUITE: "%s.%s" % (instance.__class__.__module__, name),
                    tags.TEST_NAME: instance._testMethodName,
                    tags.TEST_CODE: code,
                }) as scope:
            scope.span.context.baggage[tags.TRACE_KIND] = tags.TEST
            return wrapped(TestResultProxy(result, scope.span))

    try:
        logger.debug("patching module=unittest name=TestCase")
        wrapt.wrap_function_wrapper('unittest', 'TestCase.run', wrapper)
    except ImportError:
        logger.debug("module not found module=unittest")
