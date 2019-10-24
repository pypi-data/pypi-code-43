import logging
from functools import wraps
from django.conf import settings


def process_dynamic_log_level(request):
    logger = logging.getLogger("django.request")
    urllib3_logger = logging.getLogger("urllib3")
    if settings.NIM_DJANGO_REQUEST_LOG_LEVEL_NAME in request.META:
        level_value = request.META.get(settings.NIM_DJANGO_REQUEST_LOG_LEVEL_NAME).upper()
        if level_value in settings.ALLOWED_DYNAMIC_DEBUG_LEVEL_VALUES:
            logger.setLevel(level_value)
            urllib3_logger.setLevel(level_value)
            logger.info("The header '{}' has been overwritten to the value {}".format(
                settings.NIM_DJANGO_REQUEST_LOG_LEVEL_NAME, level_value))
        else:
            logger.info("The header '{}' has an invalid value, the values allowed are {}".format(
                settings.NIM_DJANGO_REQUEST_LOG_LEVEL_NAME, ", ".join(settings.ALLOWED_DYNAMIC_DEBUG_LEVEL_VALUES)))


def dynamic_log_level():
    def _dynamic_log_level(func):  # pragma: no cover
        def dynamic_log_level_logic(*argv, **kwargs):
            if "request" in kwargs:
                request = kwargs["request"]
                process_dynamic_log_level(request)
            elif len(argv) > 1: #The first argument is the Django Rest HTTP request
                request = argv[1]
                process_dynamic_log_level(request)
            return func(*argv, **kwargs)

        return wraps(func)(dynamic_log_level_logic)

    return _dynamic_log_level
