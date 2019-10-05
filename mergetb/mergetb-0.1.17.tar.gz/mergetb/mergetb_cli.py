#!/usr/bin/env python3

import argparse
from argparse import RawTextHelpFormatter

import logging
from os.path import expanduser, exists as path_exists
import yaml

from pygments import highlight, lexers, formatters

import mergetb.lib as mergelib
from mergetb.cli import CliToken, request_token_to, MergeApiCliException
from mergetb.utils import add_logging_args, handle_logging_args, get_function, valid_cmds

log = logging.getLogger(__name__)

DESC = '''
Command line interface to the mergetb API. To login, run with -l user@address. This 
will create and store a temporary authorization token in the given token-path.
    
Run with optional arugments above and then a subject verb. To see help for an individual
command run: "[subject] help" "[subject verb] help" Valid commands are:\n\n

login emailaddress
{}
'''.format('\n'.join(valid_cmds()))

def main():
    ap = argparse.ArgumentParser(description=DESC, formatter_class=RawTextHelpFormatter)
    ap.add_argument('-p', '--password', default=None,
                    help='Use the password given when executing a --login. If not given, '
                    'it will be prompted for.')
    ap.add_argument('-P', '--token-path', dest='token_path',
                    default=expanduser('~')+"/.merge/cli_token",
                    help='Path to read or write the API access token to or from. If not given, '
                    '~/.merge/cli_token will be used.')
    ap.add_argument('-a', '--api', dest='api', default='api.mergetb.net',
                    help='If given, use the address for the merge API. Defaults to api.mergetb.net')
    ap.add_argument('-u', '--url', type=str, help="The API path to read", default='health')
    ap.add_argument('-c', '--merge-api-cert', type=str, dest='apicert',
                    help='Path to certificate of the Merge API endpoint. Can also be specified by '
                    'setting the MERGE_API_CERT environment variable.')
    ap.add_argument('subject', nargs='?', help='The thing to view or modify.')
    ap.add_argument('verb', nargs='?', help='The action to apply to the subject.')
    ap.add_argument('args', nargs=argparse.REMAINDER,
                    help='variable number of possibly optional arguments.')

    add_logging_args(ap)
    args = ap.parse_args()
    handle_logging_args(args)

    if args.subject == 'login':
        try:
            request_token_to(args.token_path, args.verb, args.password)
        except MergeApiCliException as e:
            print('Error logging in: {}'.format(e))
            exit(666)
        exit(0)

    usage, func, func_args = get_function(args.subject, args.verb, args.args)
    log.debug('\nusage: %s\nfunc: %s\nargs: %s\n', usage, func, func_args)
    args = ap.parse_args()

    if not func:
        print('Usage: {}'.format(usage))
        exit(1)

    if not path_exists(args.token_path):
        if 'login' not in args or not args.login:
            print("Please login before executing commands.")
            exit(668)
        try:
            request_token_to(args.token_path, args.login, args.password)
        except MergeApiCliException as e:
            print('Error logging in: {}'.format(e))
            exit(666)

        log.info('wrote access token to %s', args.token_path)

    with CliToken(args.token_path, args.apicert) as token:
        mergelib.set_token(token)
        mergelib.set_api(args.api)
        resp = func(*func_args)
        if isinstance(resp, int):
            print('response: {}'.format(resp))
        elif isinstance(resp, str):
            print(resp)
        else:
            ya = yaml.dump(resp, default_flow_style=False)
            syntax = highlight(
                ya,
                lexers.YamlLexer(),
                formatters.Terminal256Formatter(bg="dark")
            )
            print(syntax)

        exit(0)

if __name__ == "__main__":
    main()
