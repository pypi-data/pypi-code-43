#!/usr/bin/env python3

""" Print Hello World."""

import pyCommonTools as pct


def hello_world(name='World'):

    log = pct.create_logger()

    print(f'Hello {name}.')
    log.debug(f"Printed 'Hello {name}.'")
