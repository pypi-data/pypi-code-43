#!/usr/bin/env python3

"""
Support for managing RBAC permissions and roles (e.g. AWS IAM) to support applying blueprints.

Usage: role [-r <role>] [assume|init|destroy]

e.g.

* assumerole -r bedrock-blueprint-admin
* assumerole --duration 1800 # 30 minutes
"""
import argparse

import sys


class BedrockRole:

    def __init__(self, args):
        parser = argparse.ArgumentParser(description='Bedrock Assume Role Tool.')
        parser.add_argument('-r', '--role', metavar='<iam_role>', help='optional role to assume')
        parser.add_argument('-d', '--duration', metavar='<session_duration>', help='optional session duration')

        parsed_args = parser.parse_args(args)


if __name__ == "__main__":
    BedrockRole(sys.argv)
