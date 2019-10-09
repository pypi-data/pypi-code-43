import logging
from functools import wraps

import opentracing
from opentracing.ext import tags

logger = logging.getLogger(__name__)


def wrap_wsgi(other_wsgi, tracer):
    @wraps(other_wsgi)
    def wsgi_tracing_middleware(environ, start_response):
        logger.debug("request intercepted environ=%s", environ)
        try:
            context = tracer.extract(format=opentracing.Format.HTTP_HEADERS, carrier=extract_headers(environ))
        except opentracing.SpanContextCorruptedException:
            context = None

        # Use dictionary to get around lack of 'nonlocal' keyword in Python 2.7
        status_code = {'status': None}

        def _start_response(status, headers, *args, **kwargs):
            # Status is a string like "200 OK".
            # See https://www.python.org/dev/peps/pep-0333/#the-start-response-callable
            # Convert to int as expected in OpenTracing.
            code = int(status.split()[0])
            status_code['status'] = code
            return start_response(status, headers, *args, **kwargs)

        with tracer.start_active_span(
            child_of=context,
            operation_name="HTTP %s" % environ['REQUEST_METHOD'],
            tags=tags_from_environ(environ),
        ) as scope:
            # "ret" may be an instance of "werkzeug.wsgi.ClosingIterator" (e.g. when using gunicorn),
            # and there doesn't seem to be any good way of getting info out of that.
            # So we grab the status code by wrapping the "start_response" instead.
            ret = other_wsgi(environ, _start_response)
            if status_code['status']:
                scope.span.set_tag(tags.HTTP_STATUS_CODE, status_code['status'])
                if status_code['status'] >= 400:
                    scope.span.set_tag(tags.ERROR, True)
            return ret
    return wsgi_tracing_middleware


def extract_headers(request):
    prefix = 'HTTP_'
    p_len = len(prefix)
    headers = {
        key[p_len:].replace('_', '-').lower():
            val for (key, val) in request.items()
        if key.startswith(prefix)
    }
    return headers


def tags_from_environ(environ):
    # WSGI reference: https://www.python.org/dev/peps/pep-3333/
    span_tags = {
        tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER,
        tags.HTTP_URL: "%(wsgi.url_scheme)s://%(HTTP_HOST)s%(PATH_INFO)s%(QUERY_STRING)s" % environ,
        tags.HTTP_METHOD: environ['REQUEST_METHOD'],
    }
    if 'REMOTE_ADDR' in environ:
        span_tags[tags.PEER_HOST_IPV4] = environ['REMOTE_ADDR']
    if 'REMOTE_PORT' in environ:
        span_tags[tags.PEER_PORT] = environ['REMOTE_PORT']
    if 'REMOTE_HOST' in environ:
        span_tags[tags.PEER_HOSTNAME] = environ['REMOTE_HOST']
    if 'REMOTE_ADDR' in environ and 'REMOTE_PORT' in environ:
        span_tags[tags.PEER_ADDRESS] = "%(REMOTE_ADDR)s:%(REMOTE_PORT)s" % environ
    return span_tags
