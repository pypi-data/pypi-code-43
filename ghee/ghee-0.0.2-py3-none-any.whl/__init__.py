name = "ghee"
__version__ = '0.0.2'

import sys
import pathlib

from .ghee import Ghee


def get_from_config(filename):
    try:
        config_file_path = next(pathlib.Path.home().glob(f'.{filename}.ghee'))
    except StopIteration:
        raise ValueError(f'There is no {pathlib.Path.home()}/.{filename}.ghee file!')
    config_file = open(config_file_path).read().rstrip()
    return Ghee(config_file)


def get_default():
    return get_from_config('default')


def send_via_default_config_url():
    _, *message = sys.argv
    message = ' '.join(message)
    echo = get_default()
    print(f'Sending: {message}')
    print(f'Via: {echo.url.geturl()}')
    print(echo(message))


def send_via_custom_url():
    _, url, *message = sys.argv
    message = ' '.join(message)
    print(f'Sending: {message}')
    print(f'Via: {url}')
    echo = Ghee(url)
    print(echo(message))