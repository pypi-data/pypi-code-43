import logging

import six
import wrapt

from . import run_once
from ..tracer import tags
from ..tracer.exception import get_exception_log_fields

logger = logging.getLogger(__name__)

# Save a set of "normal" fields so we can determine which fields are "extra"
STANDARD_FIELDS = set(logger.makeRecord(__name__, logging.INFO, None, 0, "", (), None).__dict__.keys())


@run_once
def patch(tracer):
    def wrapper(wrapped, instance, args, kwargs):
        record = args[0] if len(args) >= 1 else kwargs.get('record')
        if not record.name.startswith('scopeagent'):
            logger.debug("intercepting request: instance=%s args=%s kwargs=%s", instance, args, kwargs)
            active_span = tracer.active_span
            if active_span:
                kv = {
                    tags.EVENT: 'log',
                    tags.MESSAGE: record.getMessage(),
                    tags.LOG_LOGGER: record.name,
                    tags.LOG_LEVEL: record.levelname,
                    tags.SOURCE: '{}:{}'.format(record.pathname, record.lineno),
                }
                if record.exc_info:
                    kv.update(get_exception_log_fields(*record.exc_info))
                # stack_info doesn't exist in Python 2.7
                if six.PY3 and record.stack_info:
                    kv.update({
                        tags.STACK: record.stack_info,
                    })
                # Try to capture values passed as "extra"
                # e.g.: logger.info("This is a user", extra={'user': 'bob', 'favorite_color': "blue"})
                extra_keys = set(record.__dict__.keys()) - STANDARD_FIELDS
                for key in extra_keys:
                    kv[key] = getattr(record, key)

                active_span.log_kv(kv, timestamp=record.created)
        return wrapped(*args, **kwargs)

    try:
        logger.debug("patching module=logging name=StreamHandler.emit")
        wrapt.wrap_function_wrapper('logging', 'StreamHandler.emit', wrapper)
    except ImportError:
        logger.debug("module not found module=logging")
