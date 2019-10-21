from functools import wraps
import logging

from django.http import HttpResponse

from .helpers import _ensure_request

logger = logging.getLogger('typeform')


def ensure_request(view_func):
    """
    Decorator that ensure request from typeform.
    """
    @wraps(view_func)
    def _wrapped_view_func(request, *args, **kwargs):
        logger.info('Typeform request received')
        if not _ensure_request(request):
            return HttpResponse('')
        else:
            return view_func(request, *args, **kwargs)
    return _wrapped_view_func
