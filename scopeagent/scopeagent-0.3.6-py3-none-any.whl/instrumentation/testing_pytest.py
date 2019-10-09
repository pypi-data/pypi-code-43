import inspect
import logging

import wrapt

from scopeagent.tracer import tags
from . import run_once

logger = logging.getLogger(__name__)


@run_once
def patch(tracer):
    def wrapper(wrapped, instance, args, kwargs):
        logger.debug("intercepting test: instance=%s args=%s kwargs=%s", instance, args, kwargs)
        testfn = args[0].obj

        try:
            file = inspect.getsourcefile(testfn)
            file = file.lstrip('/')
            lines, first_line = inspect.getsourcelines(testfn)
            code = "%s:%d:%d" % (file, first_line, first_line + len(lines))
        except (IOError, OSError,):
            code = ""

        with tracer.start_active_span(
                operation_name=testfn.__name__,
                tags={
                    tags.SPAN_KIND: tags.TEST,
                    tags.TEST_FRAMEWORK: 'pytest',
                    tags.TEST_SUITE: testfn.__module__,
                    tags.TEST_NAME: testfn.__name__,
                    tags.TEST_CODE: code,
                }) as scope:
            scope.span.context.baggage[tags.TRACE_KIND] = tags.TEST
            results = wrapped(*args, **kwargs)
            for result in results:
                if result.outcome == 'failed':
                    scope.span.set_tag(tags.TEST_STATUS, tags.TEST_STATUS_FAIL)
                    scope.span.set_tag(tags.ERROR, True)
                    logger.debug(type(result.longrepr))
                    break
                elif result.outcome == 'skipped':
                    scope.span.set_tag(tags.TEST_STATUS, tags.TEST_STATUS_SKIP)
                    break

            if tags.TEST_STATUS not in scope.span.tags:
                scope.span.set_tag(tags.TEST_STATUS, tags.TEST_STATUS_PASS)

            return results

    try:
        logger.debug("patching module=_pytest.runner name=runtestprotocol")
        wrapt.wrap_function_wrapper('_pytest.runner', 'runtestprotocol', wrapper)
    except ImportError:
        logger.debug("module not found module=_pytest.runner")
