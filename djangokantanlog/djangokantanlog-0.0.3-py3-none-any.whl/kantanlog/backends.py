# -*- coding: utf8 -*-
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class KantanlogDefaultBackend:

    def __init__(self):

        required_middleware = 'kantanlog.middlewares.KantanlogMiddleware'
        middlewares = settings.MIDDLEWARE

        if required_middleware not in middlewares:
            raise ImproperlyConfigured(
                'Error "%s" is not found in MIDDLEWARE_CLASSES nor MIDDLEWARE. ' # noqa
                'It is required to use KantanlogDefaultBackend' % required_middleware, # noqa
            )

    def get_user(self, request):
        if request is None or (not hasattr(request, 'user')):
            return None
        return request.user
