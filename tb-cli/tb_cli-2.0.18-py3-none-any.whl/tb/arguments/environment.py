from functools import wraps

from tb import Tb
from .validators import validate_attribute

arguments = [
    (['-e', '--environment'],
     dict(help='environment override',
          action='store',
          nargs='?',
          dest='env')),
]


def validate(func):
    @wraps(func)
    def wrapper(controller, *args, **kwargs):
        process_parsed_arguments(controller.app)
        func(controller, *args, **kwargs)

    return wrapper


def process_parsed_arguments(app: Tb):
    validate_attribute(app, 'env', '-e/--environment', app.environments)

    if not app.pargs.env and app.environments:
        app.pargs.env = next(iter(app.environments.keys()))
