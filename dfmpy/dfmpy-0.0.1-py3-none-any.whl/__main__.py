#!/usr/bin/env python3

# TODO docs

import logging
from argparse import ArgumentParser
from logging import StreamHandler
from logging import getLogger
from sys import stdout

from dfmpy.commands.initialize import initialize
from dfmpy.commands.ls import ls
from dfmpy.commands.remove import remove
from dfmpy.commands.sync import sync
from dfmpy.utils.interactive import check_for_interactivity
from dfmpy.utils.logging import get_formatter

# TODO docs
LOG = getLogger()

# TODO docs
__LOG_LEVELS = tuple([
    logging.CRITICAL,
    logging.ERROR,
    logging.WARNING,
    logging.INFO,
    logging.DEBUG,
])


def __setup_logger(verbosity_index=None):
    # TODO docs
    # TODO unit test
    if not verbosity_index:
        verbosity_index = 1
    verbosity_index = max(0, min(len(__LOG_LEVELS) - 1, verbosity_index))
    log_level = __LOG_LEVELS[verbosity_index]
    # formatter = Formatter('%(asctime)s %(levelname)s %(message)s')
    formatter = get_formatter('%(levelname)s %(message)s')
    handler = StreamHandler(stdout)
    handler.setFormatter(formatter)
    logger = getLogger()
    logger.setLevel(log_level)
    logger.addHandler(handler)


def __parse_arguments():
    # TODO docs
    # TODO unit test

    verbose_args = tuple(['-v', '--verbose'])
    verbose_kwargs = {
        'action': 'count',
        'default': 1,
        'help': 'Set verbosity level, multiple flags increase the level.',
    }
    force_args = tuple(['-f', '--force'])
    force_kwargs = {
        'action': 'store_true',
        'default': False,
        'dest': 'force',
    }
    interactive_args = tuple(['-i', '--interactive'])
    interactive_kwargs = {
        'action': 'store_true',
        'default': False,
        'dest': 'interactive',
    }

    parser = ArgumentParser(prog='dfmpy')
    parser.add_argument(*verbose_args, **verbose_kwargs, dest='main_verbosity')
    subparsers = parser.add_subparsers(help='sub-command help')

    init_parser = subparsers.add_parser('init',
                                        aliases=tuple(['i']),
                                        help='initialize help')
    init_parser.set_defaults(func=initialize)
    init_parser.add_argument(*verbose_args,
                             **verbose_kwargs,
                             dest='verbosity')
    init_parser.add_argument(*force_args,
                             **force_kwargs,
                             help='Force overwriting of files.')
    init_parser.add_argument(*interactive_args,
                             **interactive_kwargs,
                             help='Interactively overwrite files if there are'
                                  ' conflicts.')

    ls_parser = subparsers.add_parser('list',
                                      aliases=tuple(['ls']),
                                      help='list help')
    ls_parser.set_defaults(func=ls)
    ls_parser.add_argument(*verbose_args, **verbose_kwargs, dest='verbosity')

    sync_parser = subparsers.add_parser('sync',
                                        aliases=tuple(['s']),
                                        help='sync help')
    sync_parser.set_defaults(func=sync)
    sync_parser.add_argument(*verbose_args,
                             **verbose_kwargs,
                             dest='verbosity')
    sync_parser.add_argument(*force_args,
                             **force_kwargs,
                             help='Overwrite files if there are conflicts.')
    sync_parser.add_argument(*interactive_args,
                             **interactive_kwargs,
                             help='Interactively overwrite files if there are'
                                  ' conflicts.')

    remove_parser = subparsers.add_parser('remove',
                                          aliases=tuple(['rm']),
                                          help='remove help')
    remove_parser.set_defaults(func=remove)
    remove_parser.add_argument(*verbose_args,
                               **verbose_kwargs,
                               dest='verbosity')
    remove_parser.add_argument(*force_args,
                               **force_kwargs,
                               help='Force removal of files.')
    remove_parser.add_argument(*interactive_args,
                               **interactive_kwargs,
                               help='Interactively remove of files.')

    args = parser.parse_args()
    if not hasattr(args, 'func'):
        parser.print_help()
        parser.exit()

    # Since a argument cannot exist on both the main parser as well as a
    # sub-parser we need to normalize here.  They technically can both exist,
    # but the sub-parser overwrites any value calculated from parsing the main
    # arguments.
    if 'main_verbosity' in args:
        args.verbosity += args.main_verbosity - 1

    return args


def main():
    # TODO docs
    # TODO unit test?
    args = __parse_arguments()
    __setup_logger(args.verbosity)
    try:
        LOG.debug('Arguments: %s', args)

        if 'interactive' in args \
                and args.interactive \
                and not check_for_interactivity():
            raise RuntimeError(
                'Cannot run interactively while not attached to a TTY.')

        args.func(args)

    except KeyboardInterrupt:
        print('')
        LOG.warning('Leaving dfmpy prematurely.')

    # except Exception as e:
    #     LOG.critical(e)
    #     LOG.exception(e)

    except BaseException as e:
        # LOG.critical(e)
        LOG.exception(e)


if __name__ == '__main__':
    main()
