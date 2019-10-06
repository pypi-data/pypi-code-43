"""
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
"""

import os
import tvdb_api
from typing import Dict, Any
from colorama import Fore, Back, Style
from toktokkie.metadata.Metadata import Metadata
from toktokkie.renaming.Renamer import Renamer
from anime_list_apis.api.AnilistApi import AnilistApi


class Checker:
    """
    Class that performs checks on Metadata objects
    """

    def __init__(
            self,
            metadata: Metadata,
            show_warnings: bool,
            fix_interactively: bool,
            config: Dict[str, Any]
    ):
        """
        Initializes the checker
        :param metadata: The metadata to check
        :param show_warnings: Whether or not to show warnings
        :param fix_interactively: Can be set to True to
                                  interactively fix some errors
        :param config: A dictionary containing configuration options
        """
        self.metadata = metadata
        self.show_warnings = show_warnings
        self.fix_interactively = fix_interactively
        self.config = config
        self.tvdb = config.get("tvdb_api", tvdb_api.Tvdb())
        self.anilist_user = config.get("anilist_user")
        self.anilist_api = config.get("anilist_api", AnilistApi())
        self.anilist_anime_list = config.get("anilist_anime_list", [])
        self.anilist_manga_list = config.get("anilist_manga_list", [])

    def check(self) -> bool:
        """
        Performs sanity checks and prints out anything that's wrong
        :return: The result of the check
        """
        print("-" * 80)
        print("Checking {}".format(self.metadata.name))
        valid = self._check_icons()
        valid = self._check_renaming() and valid
        return valid

    def _check_icons(self) -> bool:
        """
        Checks that the icon directory exists and there's an icon file for
        every child directory as well as the main directory.
        :return: The result of the check
        """
        valid = True

        if not os.path.isdir(self.metadata.icon_directory):
            valid = self.error("Missing icon directory")

        main_icon = os.path.join(self.metadata.icon_directory, "main.png")
        if not os.path.isfile(main_icon):
            valid = self.error("Missing main icon file for {}".format(
                self.metadata.name
            ))

        for child in os.listdir(self.metadata.directory_path):
            child_path = os.path.join(self.metadata.directory_path, child)
            if child.startswith(".") or not os.path.isdir(child_path):
                continue
            else:
                icon_file = os.path.join(
                    self.metadata.icon_directory, child + ".png"
                )
                if not os.path.isfile(icon_file):
                    valid = \
                        self.error("Missing icon file for {}".format(child))

        return valid

    def _check_renaming(self) -> bool:
        """
        Checks if the renaming of the files and directories of the
        metadata content is correct and up-to-date
        :return: The result of the check
        """
        valid = True
        renamer = Renamer(self.metadata)

        has_errors = False
        for operation in renamer.operations:
            if operation.source != operation.dest:
                valid = self.error("File Mismatch:")
                print("{}{}{}".format(
                    Fore.LIGHTGREEN_EX,
                    os.path.basename(operation.source),
                    Style.RESET_ALL
                ))
                print("{}{}{}".format(
                    Fore.LIGHTCYAN_EX,
                    os.path.basename(operation.dest),
                    Style.RESET_ALL
                ))
                has_errors = True

        if has_errors and self.fix_interactively:
            renamer.rename(False)
            return True
        else:
            return valid

    # noinspection PyMethodMayBeStatic
    def error(self, text: str) -> bool:
        """
        Prints a black-on-red error message
        :param text: The text to print
        :return: False
        """
        print("{}{}{}{}".format(Back.RED, Fore.BLACK, text, Style.RESET_ALL))
        return False

    def warn(self, text: str) -> bool:
        """
        Prints a black-on-yellow warning message
        :param text: The text to print
        :return: True if not showing warnings, else False
        """
        if self.show_warnings:
            print("{}{}{}{}".format(
                Back.YELLOW, Fore.BLACK, text, Style.RESET_ALL
            ))
        return not self.show_warnings
