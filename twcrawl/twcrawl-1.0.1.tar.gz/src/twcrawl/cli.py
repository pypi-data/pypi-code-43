#!/usr/bin/env python

import asyncio
import argparse
from .crawler import crawl
from .models import init_models


def main():
    """The main of the CLI tool."""
    parser = setup_argparse()
    args = parser.parse_args()
    if args.init:
        init_models()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawl(args))
    loop.close()


def setup_argparse():
    """Prepares the parser for this CLI tools main."""
    parser = argparse.ArgumentParser(
        description="Crawls most influential users on Twitter and downloads their statuses."
    )
    parser.add_argument(
        "-i",
        "--init",
        action="store_true",
        help="create empty SQLite3 db before start crawling"
    )
    parser.add_argument(
        '--users',
        metavar='FILE',
        type=argparse.FileType('r'),
        help='file containing screen names of users to start crawling from'
    )
    return parser


if __name__ == '__main__':
    main()
