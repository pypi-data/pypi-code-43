# TODO docs

from logging import Formatter
from sys import stdout

from termcolor import colored


class NonColoredFormatter(Formatter):
    # TODO docs

    def format(self, record):
        # TODO docs
        # TODO unit test
        record.levelname = '[' + record.levelname[0] + ']'
        formatted_msg = super(NonColoredFormatter, self).format(record)
        return formatted_msg


class ColoredFormatter(NonColoredFormatter):
    # TODO docs

    # TODO docs - sub-dict args should match colored() args
    _COLORS = {
        'CRITICAL': {'color': 'white',
                     'on_color': 'on_red',
                     'attrs': tuple(['bold'])},
        'FATAL': {'color': 'white',
                  'on_color': 'on_red',
                  'attrs': tuple(['bold'])},
        'ERROR': {'color': 'red'},
        'WARNING': {'color': 'yellow'},
        'INFO': {'color': 'cyan'},
        'DEBUG': {},
    }

    def format(self, record):
        # TODO docs
        # TODO unit test
        # TODO move from termcolor to coloraama?
        # https://pypi.org/project/termcolor/
        # https://pypi.org/project/colorama/
        colors = ColoredFormatter._COLORS[record.levelname]
        formatted_msg = super(ColoredFormatter, self).format(record)
        colored_msg = colored(formatted_msg, **colors)
        return colored_msg


def get_formatter(*args, **kwargs):
    # TODO docs
    # TODO unit test
    if stdout.isatty():
        return ColoredFormatter(*args, **kwargs)
    else:
        return NonColoredFormatter(*args, **kwargs)
