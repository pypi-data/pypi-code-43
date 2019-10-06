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
from xdcc_dl.helper import set_logging_level, set_throttle_value
from toktokkie.scripts.Command import Command
from toktokkie.xdcc_update.XDCCUpdater import XDCCUpdater
from toktokkie.exceptions import MissingXDCCInstructions, \
    InvalidXDCCInstructions


class XdccUpdateCommand(Command):
    """
    Class that encapsulates behaviour of the xdcc-update command
    """

    @classmethod
    def name(cls) -> str:
        """
        :return: The command name
        """
        return "xdcc-update"

    @classmethod
    def prepare_parser(cls, parser: argparse.ArgumentParser):
        """
        Prepares an argumentparser for this command
        :param parser: The parser to prepare
        :return: None
        """
        cls.add_directories_arg(parser)
        parser.add_argument("-t", "--throttle",
                            help="Limits the download speed of xdcc-dl. "
                                 "Append K,M or G for more convenient units")
        parser.add_argument("--create", action="store_true",
                            help="If this flag is set, "
                                 "will generate new xdcc update instructions")

    def execute(self):
        """
        Executes the commands
        :return: None
        """
        for directory in self.load_directories(self.args.directories):
            try:
                if self.args.create:
                    XDCCUpdater.prompt(directory.metadata)
                else:
                    set_logging_level(
                        self.args.quiet,
                        self.args.verbose,
                        self.args.debug
                    )
                    set_throttle_value(self.args.throttle)
                    directory.xdcc_update()

            except MissingXDCCInstructions:
                print("No XDCC update instructions for {}"
                      .format(directory.path))
            except InvalidXDCCInstructions:
                print("Invalid XDCC update instructions for {}"
                      .format(directory.path))
