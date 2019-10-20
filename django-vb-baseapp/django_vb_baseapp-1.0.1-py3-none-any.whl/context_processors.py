# pylint: disable=W0613

import os

__all__ = ['django_environment_variable']


def django_environment_variable(request):
    return {'DJANGO_ENV': os.environ.setdefault('DJANGO_ENV', 'development')}
