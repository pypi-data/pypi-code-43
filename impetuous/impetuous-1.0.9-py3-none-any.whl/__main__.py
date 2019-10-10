#!/usr/bin/env python3
"""
Wow, look at all these things you can do!
"""

import argparse
import asyncio
import gettext
import logging
import os
import pdb
import textwrap
from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentParser,
    FileType,
    Namespace,
    RawDescriptionHelpFormatter,
)
from datetime import datetime, time, timedelta
from functools import partial
from pathlib import Path

import colorama as ca

from impetuous import __version__ as version
from impetuous.cli import parse_friendly_datetime
from impetuous.cli.actions import (
    ACTION_DEST,
    Cli,
    DryRun,
    im_a,
    im_config_edit,
    im_decode,
    im_doing,
    im_edit,
    im_encode,
    im_export,
    im_import,
    im_import_legacy,
    im_post,
    im_repl,
    im_show,
    im_suggest,
    im_summary,
)
from impetuous.config import CONFIG_INI_PATH
from impetuous.data import DATA_PATH, soften_datetime
from impetuous.im import Impetuous
from impetuous.interaction import OperationError, RequestError
from impetuous.sheet import localtz, utcnow

logger = logging.getLogger("impetuous")


def friendly_datetime(*args, **kwargs):
    """
    Calls parse_friendly_datetime but modifies resolution of returned datetime
    to be compatable with how we serialize it for the database I guess...
    """
    return soften_datetime(parse_friendly_datetime(*args, **kwargs))


def main():
    # Localization? Maybe?
    import os.path

    ld = os.path.join(os.path.dirname(__file__), "..", "locale")
    gettext.install("impetuous", ld)

    today = utcnow().astimezone(localtz).date()
    # If these are strings, their type is called on them before being assigned to the
    # namespace, unfortunately, this till doesn't change the displayed defaults when you
    # run "--help" with "--yesterday" ...
    default_since = "today"  # datetime.combine(today, time(0))
    default_until = "tomorrow"  # default_since + timedelta(days=1)

    args = Namespace()

    datetime_with_yesterday = lambda *a, **kw: friendly_datetime(*a, **kw) - timedelta(
        days=args.yesterday
    )
    datetime_with_yesterday.__name__ = "super cool datetime"

    class formatter_class(RawDescriptionHelpFormatter, ArgumentDefaultsHelpFormatter):
        @property
        def _width(self):
            return cli.terminal_width

        @_width.setter
        def _width(self, _):
            "No thanks..."

    # Some arguments we want to know earlier, but we don't want
    # parse_known_args to throw up if it sees '-h', so we create a parser with
    # add_help=False, then add help later on after parsing early arguments.
    parser = ArgumentParser(formatter_class=formatter_class, add_help=False)
    parser.add_argument(
        "--dbecho",
        action="store_true",
        default=False,
        help="Show everything that sqlalchemy is doing. You almost never want to do this.",
    )
    parser.add_argument(
        "--log",
        help="Logging level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="WARNING",
    )
    parser.add_argument(
        "--since",
        help="Operate on entries in progress or end on or after...",
        type=datetime_with_yesterday,
        default=default_since,
    )
    parser.add_argument(
        "--until",
        help="Operate on entries that start before ...",
        type=datetime_with_yesterday,
        default=default_until,
    )
    parser.add_argument(
        "-y",
        "--yesterday",
        help="Move the default date for most things back a day. Can be repeated.",
        action="count",
        default=0,
    )
    parser.add_argument("-d", "--debug", action="store_true", default=False)
    args, args_remaining = parser.parse_known_args(namespace=args)

    # Initialize colorama stuff
    ca.init()

    logging.basicConfig(level=getattr(logging, args.log))
    # logging.getLogger("alembic").setLevel(logging.WARNING)

    # Maybe yesterday should only affect the default? So not the these values
    # when explicitly stated?
    # args.since -= timedelta(days=args.yesterday)
    # args.until -= timedelta(days=args.yesterday)

    logger.debug("Arguments are %s", args)

    try:
        impetuous = Impetuous(dbecho=args.dbecho)
        cli = Cli(impetuous)
    except BrokenPipeError:
        pass
    except KeyboardInterrupt:
        logger.info("Bye!")
    except SystemExit:
        raise
    except Exception as e:
        if args.debug:
            logger.exception(e)
            pdb.post_mortem()
        raise

    parser.description = textwrap.dedent(
        f"""
    {__doc__}

    EDITOR is {os.environ.get("EDITOR", "ed")}
    IM_DB is {DATA_PATH}

    (You don't want to change this.)
    IM_NOW is {cli.format_datetime_plain(utcnow())}

    Your configuration is at "{CONFIG_INI_PATH}". This is an example:

        [jira]
        api = jira
        server = https://funkymonkey.atlassian.net
        basic_auth = admin:hunter2
        pattern = ((?:FOO-\d+)|(?:BAR-\d+))

        [freshdesk]
        api = freshdesk
        server = https://funkymonkey.freshdesk.com
        api_key = xxxxxxxxxxxxxxxxxxxx
        pattern = freshdesk (\d+)
        name = sheepdesk
        abbr = 🐑
    """
    )

    try:
        parser.epilog = (Path(__file__).parent / "simple_smile").read_text()
    except Exception as exc:
        logging.debug("Couldn't load simple_smile: %s", exc)

    parser.add_argument("-h", "--help", action="help", default=argparse.SUPPRESS)
    parser.add_argument("--version", action="version", version=f"%(prog)s {version}")

    subparser = parser.add_subparsers(title="action")
    subparser.required = True
    subparser.dest = ACTION_DEST

    show_args = subparser.add_parser(
        "show",
        help=im_show.__doc__,
        aliases=["s", "l"],
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    show_args.add_argument("--reverse", "-r", action="store_true", default=False)
    show_args.add_argument("--verbose", "-v", action="store_true", default=False)
    show_args.add_argument("-l", "--limit", type=int, default=None)
    show_args.set_defaults(action=im_show)

    summary_args = subparser.add_parser(
        "summary",
        help=im_summary.__doc__,
        aliases=["ss", "ll"],
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    summary_args.add_argument("--verbose", "-v", action="store_true", default=False)
    summary_args.set_defaults(action=im_summary)

    doing_args = subparser.add_parser(
        "doing",
        help=im_doing.__doc__,
        aliases=["d", "doing"],
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    doing_args.add_argument("blah", type=str, nargs="*")
    doing_args.add_argument(
        "--when",
        "-w",
        type=datetime_with_yesterday,
        default="now",
        help="Start of period",
    )
    doing_args.add_argument("--comment", "-c", type=str)
    doing_args.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        default=False,
        help="Don't commit changes to the database. Just talk about them.",
    )
    doing_args.set_defaults(action=im_doing)

    edit_args = subparser.add_parser(
        "edit", help=im_edit.__doc__, formatter_class=ArgumentDefaultsHelpFormatter
    )
    edit_args.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        default=False,
        help="Don't commit changes to the database. Just talk about them.",
    )
    edit_args.set_defaults(action=im_edit)

    suggest_args = subparser.add_parser(
        "suggest",
        help=im_suggest.__doc__,
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    suggest_args.add_argument(
        "-l", "--limit", type=int, default=20, help="How many suggestions."
    )
    suggest_args.set_defaults(action=im_suggest)

    import_legacy_args = subparser.add_parser(
        "import-legacy",
        help=im_import_legacy.__doc__,
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    import_legacy_args.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        default=False,
        help="Don't commit changes to the database. Just talk about them.",
    )
    import_legacy_args.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="Don't output the entries as they are imported.",
    )
    import_legacy_args.add_argument(
        "--ignore-errors",
        action="store_true",
        default=False,
        help="Commit partial data, even if some stuff couldn't be inserted.",
    )
    import_legacy_args.add_argument(
        "files", default="-", nargs="+", type=argparse.FileType("r")
    )
    import_legacy_args.set_defaults(action=im_import_legacy)

    config_args = subparser.add_parser(
        "config-edit",
        help=im_config_edit.__doc__,
        aliases=["edit-config"],
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    config_args.set_defaults(action=im_config_edit)

    post_args = subparser.add_parser(
        "post", help=im_post.__doc__, formatter_class=ArgumentDefaultsHelpFormatter
    )
    post_args.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        default=False,
        help="Do not actually send submissions. Just talk about them.",
    )
    post_args.set_defaults(action=im_post)

    encode_args = subparser.add_parser(
        "encode", help=im_encode.__doc__, formatter_class=ArgumentDefaultsHelpFormatter
    )
    encode_args.add_argument(
        "codec", choices=["base64", "bz2", "hex", "quotedprintable", "uu", "zlib"]
    )
    encode_args.set_defaults(action=im_encode)

    decode_args = subparser.add_parser(
        "decode", help=im_decode.__doc__, formatter_class=ArgumentDefaultsHelpFormatter
    )
    decode_args.set_defaults(action=im_decode)

    a_args = subparser.add_parser(
        "a",
        aliases=["an"],
        help=im_a.__doc__,
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    a_args.add_argument("?", type=str, nargs="+")
    a_args.set_defaults(action=im_a)

    repl_args = subparser.add_parser(
        "repl", formatter_class=ArgumentDefaultsHelpFormatter
    )
    repl_args.set_defaults(action=im_repl)

    previous_args = args
    try:
        args = parser.parse_args(args_remaining)
    except BrokenPipeError:
        pass
    except KeyboardInterrupt:
        logger.info("Bye!")
        raise SystemExit(1)
    except SystemExit:
        raise
    except Exception as e:
        if args.debug:
            logger.exception(e)
            pdb.post_mortem()
        raise

    args.__dict__.update(previous_args.__dict__)
    action = args.action

    logger.debug("Arguments are %s", args)
    logger.info(
        "Filtering from %s until %s",
        cli.format_datetime(args.since),
        cli.format_datetime(args.until),
    )
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(action(cli, args))
    except DryRun as e:
        logger.info("Exited because dry run!")
    except RequestError as e:
        logger.error(e)
        logger.error("Tried executing: %s", e.orig.statement)
        logger.error("With: %r", e.orig.params)
        raise SystemExit(1)
    except (ValueError, OperationError) as e:
        if args.debug:
            logger.exception(e)
            pdb.post_mortem()
        else:
            logger.error(e)
        raise SystemExit(1)
    except NotImplementedError as e:
        if args.debug:
            logger.exception(e)
            pdb.post_mortem()
        else:
            logger.error("This isn't implemented: %s", e)
        raise SystemExit(1)
    except BrokenPipeError:
        pass
    except KeyboardInterrupt:
        logger.info("Bye!")
        raise SystemExit(1)
    except SystemExit:
        raise
    except Exception as e:
        if args.debug:
            logger.exception(e)
            pdb.post_mortem()
        raise
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


if __name__ == "__main__":
    main()
