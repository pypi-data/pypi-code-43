from functools import wraps

from tb import Tb
from .validators import validate_attribute

arguments = [
    (['--user'],
     dict(help='Which user',
          action='store',
          nargs='?',
          dest='user'))
]


def validate(func):
    @wraps(func)
    def wrapper(controller, *args, **kwargs):
        process_parsed_arguments(controller.app)
        func(controller, *args, **kwargs)

    return wrapper


def process_parsed_arguments(app: Tb):
    validate_attribute(app, 'user', '--user', app.people)
