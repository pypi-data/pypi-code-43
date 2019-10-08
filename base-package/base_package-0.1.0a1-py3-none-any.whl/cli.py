import argparse
import logging
from typing import List

logger = logging.getLogger('base-package')


def create_argument_parser() -> argparse.ArgumentParser:
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(
        prog='base-package',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='command line interface.',
    )
    parser.add_argument(
        '--version',
        action='store_true',
        default=argparse.SUPPRESS,
        help='print version',
    )
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parsers = [parent_parser]
    subparsers = parser.add_subparsers(help='commands')
    add_subparsers(subparsers, parents=parent_parsers)
    return parser


def add_subparsers(
    subparsers: argparse._SubParsersAction, parents: List[argparse.ArgumentParser]
):
    """Add subparsers."""
    run_parser = subparsers.add_parser(
        'run',
        parents=parents,
        conflict_handler='resolve',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help='Run command.',
    )
    run_parser.add_argument('cmd', help='command')
    run_parser.set_defaults(func=run)
    hello_parser = subparsers.add_parser(
        'hello',
        parents=parents,
        conflict_handler='resolve',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help='world.',
    )
    hello_parser.set_defaults(func=hello)


def run(args: argparse.Namespace):
    logger.info(f'running {args.cmd} ...')


def hello(args: argparse.Namespace):
    print('Hello World!')
