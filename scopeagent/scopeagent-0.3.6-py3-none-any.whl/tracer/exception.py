import traceback

from scopeagent.tracer import tags


def get_exception_log_fields(exc_type, exc_value, tb):
    if exc_type and exc_value and tb:
        structured_exc = create_exception_object(exc_type, exc_value, tb)
        return {
            tags.ERROR_KIND: exc_type.__name__,
            tags.ERROR_OBJECT: ''.join(traceback.format_exception_only(exc_type, exc_value)).strip(),
            tags.STACK: ''.join(traceback.format_tb(tb)).strip(),
            tags.EXCEPTION: structured_exc,
        }
    else:
        return {}


def create_exception_object(exc_type, exc_value, tb):
    assert exc_type and exc_value and tb
    # Create structured exception format
    # In Python 3, traceback.extract_tb returns objects with attributes name, filename, etc.,
    # but in Python 2 they are just tuples.
    frames = [
        {
            'name': frame[2],  # frame.name
            'file': frame[0],  # frame.filename
            'line': frame[1],  # frame.lineno
        }
        # Iterate frames in reverse, so most specific comes first
        for frame in reversed(traceback.extract_tb(tb))
    ]
    structured_exc = {
        'kind': exc_type.__name__,
        'message': str(exc_value),
        'stacktrace': {
            'frames': frames
        }
    }
    # Note: it sounds like python-future sets __cause__ in Python 2, but six does not
    # (see http://python-future.org/compatible_idioms.html#raising-exceptions)
    if getattr(exc_value, '__cause__', None):
        cause = exc_value.__cause__
        structured_exc['cause'] = create_exception_object(type(cause), cause, cause.__traceback__)
    return structured_exc
