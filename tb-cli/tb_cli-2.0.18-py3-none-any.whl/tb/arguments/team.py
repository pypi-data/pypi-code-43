from functools import wraps

from tb import Tb
from .validators import validate_attribute

arguments = [
    (['--team'],
     dict(help='Which Team',
          action='store',
          nargs='?',
          dest='team'))
]


def validate(func):
    @wraps(func)
    def wrapper(controller, *args, **kwargs):
        process_parsed_arguments(controller.app)
        func(controller, *args, **kwargs)

    return wrapper


def process_parsed_arguments(app: Tb):
    validate_attribute(app, 'team', '--team', app.teams)
