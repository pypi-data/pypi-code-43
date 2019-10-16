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
@click.option("--print", is_flag=True, help="Prints the twelve factors to stdout.")
def dodeka(print):
    """
    dodeka is a command line tool for tracking the degree of fulfilment of The
    Twelve-Factor App methodology. Use it in your projects to test whether they
    conform to the principles for developing solid web apps that originated
    within Heroku.
    """

    if print:
        click.echo(
            factors.generate_checklist(factors=factors.generate_factors()), nl=False
        )
