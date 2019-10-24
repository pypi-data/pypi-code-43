# TODO docs

from logging import getLogger
from sys import stdin
from sys import stdout

# TODO docs
LOG = getLogger()


def check_for_interactivity():
    # TODO docs - can't be interactive if there is no terminal to read from or write to!
    # TODO unit test
    return stdout.isatty() and stdin.isatty()


def __prompt_user(message):
    # TODO docs - does not actually check "no" responses, just for a "yes."
    # TODO unit test
    # TODO make the y/N options as method arguments
    # TODO make a "strict" method param that loops this method if a y/N option is not selected.
    response = input(f'{message} [y/N]: ').strip().lower()
    response = (response and response[0] == 'y')
    if response:
        LOG.debug('User accepted the prompt: %s', message)
    else:
        LOG.debug('User DID NOT accepted the prompt: %s', message)
    return response


def ask_to(message, force=False, interactive=True):
    # TODO docs
    # TODO unit test

    if force:
        # If "force" is true, then allow the operation.
        return True

    elif not interactive:
        # If "force" is not true, and we do not want to ask the user, then for
        # safety do not allow the operation.
        return False

    else:
        # If "force" is not true, and we want to prompt the user, then ask them
        # what to do.
        return __prompt_user(message)
