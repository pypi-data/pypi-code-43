# pylint: disable=R0903

from django.conf import settings
from django.utils import timezone

import pytz

__all__ = ['TimezoneMiddleware']


class TimezoneMiddleware:
    """
    Activate user's timezone if user has timezone field.

    add this manually to your `MIDDLEWARE` list:

    # settings/base.py

    MIDDLEWARE += [
        'vb_baseapp.middlewares.TimezoneMiddleware',
    ]

    Note:

        This middleware will be more helpfull if you use custom User model
        with `timezone` field. Check `django-timezone-field` package!

    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = settings.TIME_ZONE
        if request.user.id and getattr(request.user, 'timezone', None):
            tzname = request.user.timezone
        timezone.activate(pytz.timezone(tzname))

        response = self.get_response(request)
        return response
