"""logng.py: utilities for logging."""

import argparse
import logging
import sys

import crayons


def build_log_argp(base_parser):
    """Add an argument for logging to the base_parser."""

    class _SetLogLevel(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            conf_logging(log_level=values)
            setattr(namespace, self.dest, values)

    base_parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        action=_SetLogLevel,
    )
    return base_parser


class ColorfulLogRecord(logging.LogRecord):

    """LogRecord with colors."""

    def __init__(self, *args, **kwargs):
        # pylint: disable=no-member
        super().__init__(*args, **kwargs)
        if self.levelno == logging.CRITICAL:
            colf = crayons.red
        elif self.levelno == logging.ERROR:
            colf = crayons.magenta
        elif self.levelno == logging.WARNING:
            colf = crayons.yellow
        elif self.levelno == logging.INFO:
            colf = crayons.cyan
        else:
            colf = crayons.green
        self.levelname = str(colf(self.levelname, bold=True, always=True))

        self.msg = (
            crayons.colorama.Style.BRIGHT
            + str(self.msg)
            + crayons.colorama.Style.NORMAL
        )


def conf_logging(args=None, log_level=None):
    """Configure logging using args from `build_log_argp`."""
    if log_level is None:
        if args is not None and hasattr(args, "log_level"):
            log_level = args.log_level
        else:
            log_level = "INFO"
    log_level_i = getattr(logging, log_level, logging.INFO)

    logging.basicConfig(
        level=log_level_i,
        format="%(levelname)s:%(filename)s.%(funcName)s.%(lineno)d:%(message)s",
    )
    logging.root.setLevel(log_level_i)
    if sys.stderr.isatty():
        logging.setLogRecordFactory(ColorfulLogRecord)
