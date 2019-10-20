import sys
import argparse
from upvest_cli.config import UpvestCLIConfig
from upvest_cli.application import add_arguments as app_args, handle as app_handle
from upvest_cli.user import add_arguments as user_args, handle as user_handle


def add_arguments(parser):
    parser.add_argument(
        "--configfile",
        "-c",
        type=str,
        help="A configuration file to use to load defaults and endpoints for using the Upvest CLI.",
    )
    parser.add_argument(
        "--endpoint",
        "-e",
        type=str,
        help="Which endpoint to target with API calls. This can be a URL or a name defined in the configuration file.",
    )


def main():
    parser = argparse.ArgumentParser(prog="upvest")
    add_arguments(parser)
    subparsers = parser.add_subparsers(
        help="auth type help", description="different auth type commands", title="auth type commands"
    )

    app_args(subparsers.add_parser("app", help="application help"))
    user_args(subparsers.add_parser("user", help="user help"))

    args = parser.parse_args()

    import_from = getattr(args, "import", None)
    if args.endpoint is None and import_from is None:
        parser.error("Either --endpoint or --import mode must be specified")
        sys.exit(1)

    if import_from is not None:
        print(import_from)
        sys.exit(0)

    config = UpvestCLIConfig(args)

    authtype = getattr(args, "authtype", None)
    if authtype == "app":
        app_handle(config)
    elif authtype == "user":
        user_handle(config)
    else:
        print("Auth type must be set, app or user")
        sys.exit(1)
