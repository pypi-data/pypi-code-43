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
from toktokkie.iconizing.procedures.Procedure import Procedure


class Iconizer:
    """
    Class that handles iconizing directories
    """

    def __init__(self, path: str, icon_location: str,
                 procedure: Procedure = None):
        """
        Initializes the iconizer
        :param path: The path to the directory to iconize
        :param icon_location: The location of the icons
        :param procedure: The procedure to use for iconizing.
        """
        self.path = path
        self.icon_location = os.path.abspath(icon_location)
        self.procedure = procedure

    def iconize(self):
        """
        Iconizes the directory
        :return: None
        """
        self.procedure.iconize(
            self.path, os.path.join(self.icon_location, "main")
        )
        for child in os.listdir(self.path):
            child_path = os.path.join(self.path, child)

            if child.startswith(".") or not os.path.isdir(child_path):
                continue

            icon = os.path.join(self.icon_location, child)
            self.procedure.iconize(child_path, icon)
