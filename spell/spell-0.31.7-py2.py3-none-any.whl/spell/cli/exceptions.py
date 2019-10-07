from contextlib import contextmanager

import click
import requests.exceptions

from spell.cli.log import logger
from spell.api.exceptions import ClientException, UnauthorizedRequest
import spell.cli.utils.sentry as sentry


SPELL_INVALID_CONFIG = 2
SPELL_INVALID_WORKSPACE = 3
SPELL_INVALID_COMMIT = 4
SPELL_BAD_REPO_STATE = 5


class ExitException(click.ClickException):

    def __init__(self, message, exit_code=None):
        self.exit_code = 1 if exit_code is None else exit_code
        super(ExitException, self).__init__(message)

    def show(self):
        logger.error(self.message)


@contextmanager
def api_client_exception_handler():
    try:
        yield
    except UnauthorizedRequest:
        raise ExitException('Login session has expired. Please log in again ("spell login").')
    except ClientException as e:
        exception = getattr(e, "exception", None)
        if not exception:
            raise ExitException(e.message)
        # we expect connection errors for no internet connectivity that are not ProxyErrors or SSLErrors
        if (isinstance(exception, requests.exceptions.ConnectionError)
                and not isinstance(exception, (requests.exceptions.ProxyError, requests.exceptions.SSLError))):
            raise ExitException("Can't reach Spell. Please check your internet connection.")
        # unexpected Client Exception -- tell Spell
        sentry.capture_exception(e)
        raise ExitException(e.message)
