import importlib
from functools import wraps

import opentracing

ALL_LIBRARIES = {'server_django', 'server_flask', 'client_requests', 'client_urllib_request', 'client_kombu',
                 'app_celery', 'testing_unittest', 'testing_pytest', 'logging_logging', 'db_psycopg2'}


def run_once(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper


def patch_all(**kwargs):
    tracer = kwargs.pop('tracer', opentracing.Tracer())
    for module_name in ALL_LIBRARIES - {module_name for module_name, value in kwargs.items() if value is False}:
        module = importlib.import_module('.%s' % module_name, package=__name__)
        module.patch(tracer=tracer)
