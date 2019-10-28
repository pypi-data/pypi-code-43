#!/bin/env python

"""
pymdgen cli
"""

import argparse
import importlib
import inspect
import logging

from pymdgen import doc_module


def run(modules, debug, section_level):

    """
    run pymdgen for the specified module

    **Arguments**

    - modules (`list`): list of python module names
    - debug (`bool`): debug mode
    - section_level (`int`): header indent level to start out from

    **Returns**

    markdown lines (`list`)
    """

    if debug:
        logging.basicConfig(level=logging.DEBUG)

    output = []
    for name in modules:
        md = doc_module(name, debug=debug, section_level=section_level)
        for line in md:
            output.append(line)
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Inspects given python modules and prints markdown"
    )

    parser.add_argument(
        "--debug", dest="debug", action="store_true", help="display debug messages"
    )
    parser.add_argument(
        "--section-level", type=int, default=3, help="markdown section lavel"
    )
    parser.add_argument("modules", nargs="+")

    args = parser.parse_args()

    debug = args.debug
    modules = args.modules
    section_level = args.section_level

    for line in run(modules, debug, section_level):
        print(line)


if __name__ == "__main__":
    main()
