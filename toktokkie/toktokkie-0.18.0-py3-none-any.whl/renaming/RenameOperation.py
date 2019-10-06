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
from colorama import Fore, Style
from puffotter.os import replace_illegal_ntfs_chars


class RenameOperation:
    """
    Class that models a renaming operation
    """

    def __init__(self, source_path: str, new_name: str):
        """
        Initializes the RenameOperation object
        :param source_path: The currently existing path to the file/directory
        :param new_name: The new name of the file/directory
        """
        self.parent = os.path.dirname(source_path)
        self.source = source_path
        sanitized = self.sanitize(self.parent, new_name)
        self.dest = os.path.join(self.parent, sanitized)

    def rename(self):
        """
        Renames the episode file to the new name
        :return: None
        """
        if self.source == self.dest:
            return

        while os.path.exists(self.dest):
            print("{}Destination file '{}' already exists!{}".format(
                Fore.LIGHTRED_EX, self.dest, Style.RESET_ALL
            ))
            name, ext = self.dest.rsplit(".", 1)
            name += "_"
            self.dest = "{}.{}".format(name, ext)

        print("Renaming: {}".format(self))
        os.rename(self.source, self.dest)

    def __str__(self) -> str:
        """
        :return: A string representation of the operation
        """
        start = ""
        end = ""
        if self.source != self.dest:
            start = Fore.LIGHTYELLOW_EX
            end = Style.RESET_ALL

        return "{}{} ---> {}{}".format(start, self.source, self.dest, end)

    @staticmethod
    def sanitize(parent: str, filename: str) -> str:
        """
        Replaces all illegal file system characters with valid ones.
        Also, limits the length of the resulting file path to 250 characters,
        if at all possible
        :param parent: The parent directory
        :param filename: The filename to sanitize
        :return: The sanitized string
        """
        sanitized = replace_illegal_ntfs_chars(filename)

        try:
            name, ext = sanitized.rsplit(".", 1)
            ext = "." + ext
        except (IndexError, ValueError):
            name, ext = [sanitized, ""]

        if len(sanitized) > 250 > len(parent) + len(ext):
            max_file_length = 250 - (len(parent) + len(ext))
            name = name[0:max_file_length]

        return name + ext
