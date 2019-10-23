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
import click

from .providers import azure

# pylint and Click do not work well together in all cases, see:
# https://stackoverflow.com/questions/49680191/click-and-pylint
# pylint: disable=no-value-for-parameter
@click.group()
def interface():
    """
    agipy enables you to destroy cloud infrastructure in a hurry
    """


interface.add_command(azure.azure)


if __name__ == "__main__":
    interface()
