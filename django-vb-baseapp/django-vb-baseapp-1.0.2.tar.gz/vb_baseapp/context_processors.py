# pylint: disable=W0613

import os

from django.conf import settings
from django.utils import translation

__all__ = ['common_environment_variables']


def common_environment_variables(request):
    return {
        'DJANGO_ENV': os.environ.setdefault('DJANGO_ENV', 'development'),
        'IS_DEBUG': settings.DEBUG,
        'LANGUAGE_CODE': translation.get_language(),
    }
