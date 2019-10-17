#!/usr/bin/env python

import sys

from loguru import logger

from .cmd import CommandParser
from .utils import LazyGl, Config, validate_gitlab_auth, prompt_for_token

from .feature import Feature
from .release import Release

COMMAND_FTAB = {
    Feature.COMMAND: Feature,
    Release.COMMAND: Release,
}


def cli_entrypoint():
    parser = CommandParser()
    args = parser.parse_args()
    args.file_config = Config()

    if not args.file_config['token']:
        logger.debug('Token not found, reading it from standard input.')
        token = prompt_for_token()
        try:
            validate_gitlab_auth(token)
        except Exception:
            logger.exception('Could not validate Gitlab authentication.')
            sys.exit(1)
        args.file_config['token'] = token

    args.gl = LazyGl(args.file_config['token'])

    if args.parser_cmd is None:
        parser.print_help()
        sys.exit(1)
    elif args.parser_cmd in COMMAND_FTAB.keys():
        COMMAND_FTAB[args.parser_cmd]()(parser, args)
    else:
        logger.error('Command not implemented : {}', args.parser_cmd)
        sys.exit(1)
