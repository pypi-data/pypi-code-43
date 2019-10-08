import logging

from base_package import version
from .cli import create_argument_parser
from .utils import set_log_level, configure_colored_logging

logger = logging.getLogger(__name__)


def print_version() -> None:
    print(version.__version__)


def main() -> None:
    """Running as standalone python application."""
    import os
    import sys

    arg_parser = create_argument_parser()
    cmdline_arguments = arg_parser.parse_args()
    sys.path.insert(
        1, os.getcwd()
    )  # insert current path in syspath so custom modules are found
    log_level = cmdline_arguments.loglevel if hasattr(cmdline_arguments, 'loglevel') else None
    set_log_level(log_level)
    if hasattr(cmdline_arguments, 'func'):
        configure_colored_logging(log_level)
        cmdline_arguments.func(cmdline_arguments)
    elif hasattr(cmdline_arguments, 'version'):
        print_version()
    else:
        # user has not provided a command, let's print the help
        logger.error('No command specified.')
        arg_parser.print_help()
        exit(1)


if __name__ == '__main__':
    main()
