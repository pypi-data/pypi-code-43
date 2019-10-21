#!/usr/bin/env python3

import os
import sys
import json
import click

from demyst.cli.channel import command as channel

@click.group()
def cli():
    pass

@cli.command()
def my_first_command():
    print("LIVE")

cli.add_command(channel.channel)