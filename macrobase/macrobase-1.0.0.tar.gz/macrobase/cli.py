import argparse
import sys
from typing import List, Callable


class ArgumentParsingException(Exception):

    def __init__(self, message: str):
        self.message = message
        # print(f'{prog}: error: {message}')


class ArgumentParser(argparse.ArgumentParser):

    def error(self, message: str):
        raise ArgumentParsingException(message)


_all_key = ['all']


class CliActions:
    start = 'start'
    list = 'list'


class Cli(object):

    def __init__(self,
                 aliases: List[str],
                 action_start: Callable[[List[str]], None],
                 action_list: Callable[[List[str]], None]):
        self._aliases = aliases
        self._parser = ArgumentParser()
        subparsers = self._parser.add_subparsers(dest='action')

        start_parser = subparsers.add_parser('start')
        start_parser.add_argument(
            'drivers',
            nargs='+',
            choices=aliases + _all_key,
            help='Choose drivers names',
        )

        list_parser = subparsers.add_parser('list')
        
        self._action_start = action_start
        self._action_list = action_list

        super().__init__()

    def parse(self, argv: List[str]):
        parsed_args = self._parser.parse_args(argv)

        if parsed_args.action == CliActions.start:
            if parsed_args.drivers is None or len(parsed_args.drivers) == 0:
                raise ArgumentParsingException('Choose drivers names')

            if parsed_args.drivers == _all_key:
                self._action_start(self._aliases)
                return

            if not set(parsed_args.drivers).issubset(set(self._aliases)):
                raise ArgumentParsingException(f'No driver names for {parsed_args.name} were found\nUse \"list drivers\" to see available drivers')

            self._action_start(parsed_args.drivers)
        elif parsed_args.action == CliActions.list:
            self._action_list(self._aliases + _all_key)

    # def __call__(self, *args, **kwargs):
    #     try:
    #         parsed_args = self._parser.parse_args(self._argv)
    #     except ArgumentParsingException:
    #         sys.exit(0)
    #
    #     if parsed_args.action == CliActions.start:
    #         if hasattr(parsed_args, 'entity') and parsed_args.entity == CliActionEntities.driver:
    #
    #             if hasattr(parsed_args, 'element') and parsed_args.element is None:
    #                 print(f'Drivers need to be specified. \nUse \"list drivers\" to see available drivers')
    #             else:
    #                 # for driver in parsed_args.elements:
    #                 driver = parsed_args.element
    #                 if driver == DriverNames.sanic:
    #                     print(f'Starting {DriverNames.sanic}...')
    #                     start_sanic()
    #                 elif driver == DriverNames.all:
    #                     run_all()
    #                 elif driver == DriverNames.aiopika_server:
    #                     print(f'Starting {DriverNames.aiopika_server}...')
    #                     start_aiopika_server()
    #                 elif driver == DriverNames.aiopika_service:
    #                     print(f'Starting {DriverNames.aiopika_service}...')
    #                     start_aipika_service()
    #                 else:
    #                     print(f'No driver names for {driver} were found\nUse \"list drivers\" to see available drivers')
    #
    #     elif parsed_args.action == CliActions.list:
    #         if hasattr(parsed_args, 'entity') and parsed_args.entity == CliActionEntities.driver:
    #             print(f"Available drivers to start: \n{[n for n in dir(DriverNames) if not n.startswith('_')]}")
    #         else:
    #             print('Value expected for \"list\" command')