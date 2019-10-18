"""
agipy enables you to destroy cloud infrastructure in a hurry.
Copyright (C) 2019  Nils Müller<shimst3r@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
"""

import sys

import click

# pylint and Click do not work well together in all cases, see:
# https://stackoverflow.com/questions/49680191/click-and-pylint
# pylint: disable=no-value-for-parameter
@click.command()
@click.argument("provider", nargs=1, required=True)
@click.option(
    "-p",
    "--prefix",
    required=True,
    help="The prefix of resource groups you want to delete.",
)
def interface(provider, prefix):
    """
    interface is the entry point for the command line interface of agipy.
    """
    if provider == "azure":
        from agipy.providers import azure

        prov = azure.AzureProvider()
        prov.delete(prefix=prefix)
    else:
        click.echo(f"No provider package found for {provider}.")
        sys.exit(1)


if __name__ == "__main__":
    interface()
