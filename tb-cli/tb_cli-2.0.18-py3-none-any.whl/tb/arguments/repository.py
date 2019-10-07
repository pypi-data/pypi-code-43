import os
from functools import wraps

from tb.first_time import ensure_user_tb_config
from .validators import validate_attribute

arguments = [
    (['-r', '--repository'],
     dict(help='repository override',
          action='store',
          nargs='?',
          dest='repository')),
]


def validate(func):
    @wraps(func)
    def wrapper(controller, *args, **kwargs):
        process_parsed_arguments(controller.app)
        func(controller, *args, **kwargs)

    return wrapper


def process_parsed_arguments(app):
    ensure_user_tb_config(app.config.get_dict())
    try:
        if app.pargs.repository is None:
            for r in app.repositories.values():
                if r.name in os.path.abspath(os.path.dirname(".")).split(os.path.sep):
                    app.pargs.repository = r.name
                    break
    except AttributeError:
        return

    validate_attribute(app, 'repository', '-r/--repository', app.repositories)

    if app.pargs.repository:
        repo = next(r for r in app.repositories.values() if r.name == app.pargs.repository)

        app.term.print("<h2>{}</h2>".format("-" * 40))
        if repo:
            if app.src_dir:
                app.config.parse_file(os.path.join(app.src_dir, repo.name, '.tb.yml'))
            app.term.print(f'Current Repository: <b>{repo.name}</b>')
            app.term.print("<h2>{}</h2>".format("-" * 40))
