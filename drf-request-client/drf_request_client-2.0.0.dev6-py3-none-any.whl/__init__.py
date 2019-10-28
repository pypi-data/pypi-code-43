import os

from .drf_request_client import DRFClient


def get_version():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'VERSION')) as version_file:
        version = version_file.read().strip()
    return version


__version__ = get_version()
