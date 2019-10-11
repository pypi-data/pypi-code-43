import re
import logging

from collections import defaultdict

import colorama


class PrettyLogRecord(logging.LogRecord):
    def getPrettyMessage(self, colors):
        msg = str(self.msg)
        msg = re.sub(
            r'''(
                %
                (?:\([^)]\))?
                [-#0 +]*
                (?:\*|\d+)?
                (?:\.\*|\d+)?
                [hlL]?
                [diouxXeEfFgGcrs]
            )''',
            fr'{colors[0]}\1{colors[1]}',
            msg,
            flags=re.VERBOSE,
        )
        if self.args:
            msg = msg % self.args
        return msg


class LeveledFormatter(logging.Formatter):
    def __init__(self, fmt=None, levels_fmt=None, pretty_colors=None, levels_pretty_colors=None, *args, **kwargs):
        super().__init__(fmt, *args, **kwargs)
        self._style = self._style.__class__(fmt.format(*pretty_colors))
        levels_fmt = levels_fmt or {}
        levels_fmt = {
            **{level: fmt.format(*colors) for level, colors in levels_pretty_colors.items()},
            **levels_fmt,
        }
        self._levels_style = defaultdict(
            lambda: self._style,
            {
                key: self._style.__class__(fmt)
                for key, fmt in (levels_fmt or {}).items()
            }
        )
        self._levels_colors = defaultdict(
            lambda: pretty_colors,
            levels_pretty_colors or {}
        )

    def formatMessage(self, record):
        pretty_colors = self._levels_colors[record.levelno]
        if hasattr(record, 'getPrettyMessage') and pretty_colors:
            record.message = record.getPrettyMessage(pretty_colors)

        return self._levels_style[record.levelno].format(record)


def setup_cli_output():
    # Setup pretty command line output
    colorama.init()
    logging.setLogRecordFactory(PrettyLogRecord)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    paramiko_logger = logging.getLogger('paramiko')
    paramiko_logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler()
    handler.setFormatter(LeveledFormatter(
        fmt='[{0} {{levelname: >8}} {2}] '
            '{1}{{message}}{2}',
        pretty_colors=(colorama.Fore.YELLOW, colorama.Fore.LIGHTYELLOW_EX, colorama.Style.RESET_ALL),
        levels_pretty_colors={
            logging.INFO: (colorama.Fore.GREEN, colorama.Fore.LIGHTGREEN_EX, colorama.Style.RESET_ALL),
            logging.WARNING: (colorama.Fore.MAGENTA, colorama.Fore.LIGHTMAGENTA_EX, colorama.Style.RESET_ALL),
            logging.ERROR: (colorama.Fore.RED, colorama.Fore.LIGHTRED_EX, colorama.Style.RESET_ALL),
        },
        style='{',
    ))
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

