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
import os
import sys
import json
from PyQt5.QtWidgets import QApplication
from toktokkie.gui.MainWindow import MainWindow
from toktokkie.scripts.Command import Command


class GuiCommand(Command):
    """
    Class that encapsulates behaviour of the gui command
    """

    @classmethod
    def name(cls) -> str:
        """
        :return: The command name
        """
        return "gui"

    @classmethod
    def prepare_parser(cls, parser: argparse.ArgumentParser):
        """
        Prepares an argumentparser for this command
        :param parser: The parser to prepare
        :return: None
        """
        pass

    def execute(self):
        """
        Executes the commands
        :return: None
        """
        config_dir = os.path.join(os.path.expanduser("~"),
                                  ".config/toktokkie")
        config_file = os.path.join(config_dir, "config.json")
        if not os.path.isdir(config_dir):
            os.makedirs(config_dir)
        if not os.path.isfile(config_file):
            with open(config_file, "w") as f:
                json.dump({"media_directories": []}, f)

        app = QApplication(sys.argv)
        form = MainWindow()
        form.show()
        app.exec_()
