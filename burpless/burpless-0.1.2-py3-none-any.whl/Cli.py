#   Copyright (C) 2019  Jacopo Cascioli
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-
import click

from .Burpless import Burpless
from .Version import version


class Cli:

    @click.group()
    def main():
        pass

    @staticmethod
    @main.command()
    @click.argument('path')
    def parse(path):
        click.echo(Burpless.parse(path).pretty())

    @staticmethod
    @main.command()
    def version():
        click.echo(f'Burpless {version}')
