import argparse
import sys

from conapp.commands import apply, snapshots

COMMANDS = [
    apply,
    snapshots
]


def get_args(args: list) -> argparse.Namespace:
    """Build an argparser and return a Namespace"""

    parser = argparse.ArgumentParser(prog='conapp', description='conapp a simple Config Applier')
    parser.set_defaults(command=None)

    sub_parser = parser.add_subparsers(
        title="Commands",
        description="Valid commands",
        help="sub-command help",
    )

    for command in COMMANDS:
        command.setup_arguments(sub_parser)

    # TODO: Add other commands

    args = parser.parse_args(args=args)

    if args.command is None:
        parser.print_usage()
        sys.exit(1)
    else:
        return args
