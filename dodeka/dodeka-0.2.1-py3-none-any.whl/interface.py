"""
Copyright (c) 2019, Nils P. Müller <shimst3r@gmail.com>
All rights reserved.

This file is part of dodeka.

`interface.py` implements the command line interface. 

License: MIT, see https://opensource.org/licenses/MIT
"""
import click

from dodeka import factors


@click.command()
def dodeka():
    """
    dodeka is a command line tool for tracking the degree of fulfilment of The
    Twelve-Factor App methodology. Use it in your projects to test whether they
    conform to the principles for developing solid web apps that originated
    within Heroku.
    """
