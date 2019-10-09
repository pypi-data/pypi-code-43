# -*- coding: utf-8 -*-
# /usr/bin/env python3

import argparse
import logging
import os
from subprocess import run, PIPE

_logger = logging.getLogger(__name__)

name = "peerpkg"


def _create_file(modules):
    for root, folders, files in os.walk('.'):
        if 'sparse-checkout' not in files:
            for folder in folders:
                if folder == 'info':
                    try:
                        path = os.path.join(root, folder) + '/sparse-checkout'
                        if not os.path.exists(path):
                            with open(path, 'w') as file:
                                file.write('\n'.join(
                                    [module + "/*" for module in modules]
                                ))
                                file.close()
                    except OSError as e:
                        _logger.error("\nSomething went wrong => %s", e)

    return True


def clone(args):
    if len(args.__dict__) > 1:
        repo_url, modules = args.update, args.modules
    else:
        repo_url = args.update, modules = None

    commands_to_execute = [
        ("git", "init"),
        ("git", "remote", "add", "origin", "-f", repo_url),
        ("git", "config", "core.sparsecheckout", "true"),
        ("git", "pull", "origin", "master", "--depth=1"),
    ]

    if modules:
        modules = modules.split(',')

    for index, command in enumerate(commands_to_execute):
        try:
            if index == 3 and modules:
                _create_file(modules)
            run(command, stdout=PIPE, stderr=PIPE)
        except KeyboardInterrupt:
            _logger.error("\n%s", "Command was interrupted!")
        except Exception as e:
            _logger.error("\n%s", e)

    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u", "--update", help="Repository URL", required="True"
    )
    parser.add_argument(
        "-m", "--modules", help="Only this module(s) will be updated"
    )
    args = parser.parse_args()
    clone(args)
