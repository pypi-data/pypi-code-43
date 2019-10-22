#!/usr/bin/env python3

import argparse

import sys

from .blueprint import BedrockBlueprint, execute
from .manifest import BedrockManifest, apply


class BedrockCli(object):

    def __init__(self):
        parser = argparse.ArgumentParser(description='', usage='''bedrock <command> [<args>]
         Available commands:
            manifest    Parse and apply a Bedrock blueprint manifest
            blueprint   Apply a single Bedrock blueprint
            role  Manage/assume IAM roles used to apply blueprints
        ''')
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        getattr(self, args.command)()

    def blueprint(self):
        execute(BedrockBlueprint(sys.argv[2:]))

    def manifest(self):
        apply(BedrockManifest(sys.argv[2:]))

    # def role(self):
    #     BedrockRole(sys.argv[2:])


if __name__ == "__main__":
    BedrockCli()
