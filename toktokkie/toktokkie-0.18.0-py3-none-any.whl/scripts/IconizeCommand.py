"""LICENSE
Copyright 2015 Hermann Krumrey <hermann@krumreyh.com>

This file is part of toktokkie.

toktokkie is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

toktokkie is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with toktokkie.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

import argparse
from toktokkie.iconizing import procedures, default_procedure
from toktokkie.scripts.Command import Command


class IconizeCommand(Command):
    """
    Class that encapsulates behaviour of the iconize command
    """

    @classmethod
    def name(cls) -> str:
        """
        :return: The command name
        """
        return "iconize"

    @classmethod
    def prepare_parser(cls, parser: argparse.ArgumentParser):
        """
        Prepares an argumentparser for this command
        :param parser: The parser to prepare
        :return: None
        """
        procedure_names = set(list(map(lambda x: x.name, procedures)))

        cls.add_directories_arg(parser)
        parser.add_argument("procedure", choices=procedure_names, nargs="?",
                            default=default_procedure().name,
                            help="The procedure to use")

    def execute(self):
        """
        Executes the commands
        :return: None
        """
        procedure = list(filter(
            lambda x: x.name == self.args.procedure, procedures
        ))[0]

        for directory in self.load_directories(self.args.directories):
            try:
                directory.iconize(procedure)
            except ValueError:
                print("Iconizing of " + directory.path + "failed")
