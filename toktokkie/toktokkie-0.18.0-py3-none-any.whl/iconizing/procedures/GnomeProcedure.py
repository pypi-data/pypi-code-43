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
import sys
from subprocess import Popen, check_output, CalledProcessError
from toktokkie.iconizing.procedures.Procedure import Procedure


class GnomeProcedure(Procedure):
    """
    Iconizing Procedure that uses the gio command line tool to set the
    icon file in gnome-based systems
    """

    @classmethod
    def iconize(cls, directory: str, icon_path_no_ext):
        """
        Iconizes the directory using gio
        :param directory: The directory to iconize
        :param icon_path_no_ext: The icon file without a file extension.
                                 .png will be appended
        :return: None
        """
        icon_path = icon_path_no_ext + ".png"
        Popen([
            "gio", "set", "-t", "string", directory,
            "metadata::custom-icon", "file://" + icon_path
        ]).wait()

    @classmethod
    def is_applicable(cls) -> bool:
        """
        Checks if this procedure is applicable to the current system.
        The Gnome procedure is applicable if the system is running Linux
        as well as a Gnome environment, like the Gnome DE or Cinnamon
        :return: True if applicable, else False
        """
        path_divider = ";" if sys.platform == "win32" else ":"
        paths = os.environ["PATH"].split(path_divider)
        gvfs_installed = False
        for path in paths:
            if os.access(os.path.join(path, "gio"), os.X_OK):
                gvfs_installed = True

        gvfs_check = False
        if gvfs_installed:  # pragma: no cover

            try:
                gvfs_out = check_output([
                    "gio", "set", "-t", "string", ".",
                    "metadata::custom-icon", "a"]).decode()
            except CalledProcessError:
                gvfs_out = "Not Supported"

            if gvfs_out.rstrip().lstrip() == "":
                Popen(["gio", "set", "-t", "unset", ".",
                       "metadata::custom-icon"]).wait()
                gvfs_check = True

            try:
                return sys.platform.startswith("linux") \
                       and gvfs_installed and gvfs_check
            except KeyError:  # pragma: no cover
                return False

        else:
            return False
