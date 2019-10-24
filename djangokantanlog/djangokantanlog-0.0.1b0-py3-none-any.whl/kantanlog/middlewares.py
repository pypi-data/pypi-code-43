from logging import getLogger
from threading import local
from django.conf import settings
from django.utils.module_loading import import_string


logger = getLogger(__name__)
_thread_local = local()


_BackendClass = import_string(
    getattr(
        settings,
        'KLOG_BACKEND',
        'kantanlog.backends.KantanlogDefaultBackend'
    )
)
_backend = _BackendClass()


def get_username():
    if hasattr(_thread_local, 'user'):
        return _thread_local.user.username
    return ''


class KantanlogMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Init
        _thread_local.user = _backend.get_user(request)
        # Complete request meta
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
            request.META['REMOTE_ADDR'] = ip.strip()
        self.__writelog(request)

        response = self.get_response(request)

        del _thread_local.user
        return response

    def __writelog(self, request):
        logger.info(
            'username=%s, path=%s, method=%s, remote_addr=%s',
            get_username(),
            request.path,
            request.method,
            request.META['REMOTE_ADDR'],
        )
