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

import os
import argparse
from subprocess import Popen
from toktokkie.scripts.Command import Command
from toktokkie.metadata.components.enums import MediaType


class SetMangaCoverCommand(Command):
    """
    Class that encapsulates behaviour of the set-manga-cover command
    """

    @classmethod
    def name(cls) -> str:
        """
        :return: The command name
        """
        return "set-manga-cover"

    @classmethod
    def prepare_parser(cls, parser: argparse.ArgumentParser):
        """
        Prepares an argumentparser for this command
        :param parser: The parser to prepare
        :return: None
        """
        cls.add_directories_arg(parser)

    def execute(self):
        """
        Executes the commands
        :return: None
        """
        for directory in self.load_directories(
                self.args.directories, restrictions=[MediaType.MANGA]
        ):

            cover = os.path.join(directory.metadata.icon_directory, "main.png")
            target = os.path.join(directory.path, "cover.cbz")
            if os.path.isfile(cover):
                if not os.path.isfile(target):
                    Popen(["zip", "-j", target, cover]).wait()
            else:
                print("No cover for {}".format(directory.path))
