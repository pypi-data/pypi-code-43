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
from toktokkie.check.Checker import Checker
from toktokkie.metadata.VisualNovel import VisualNovel


class VisualNovelChecker(Checker):
    """
    Class that checks Visual Novels for consistency
    """

    def check(self) -> bool:
        """
        Performs sanity checks and prints out anything that's wrong
        :return: The result of the check
        """
        valid = super().check()
        valid = self._check_extras() and valid

        if self._check_gamefiles():
            # Requires game directory to exist
            valid = self._check_linux_drm_free_compatible() and valid
        else:
            valid = False

        return valid

    def _check_icons(self) -> bool:
        """
        Only checks for a main.png icon file.
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

        return valid

    def _check_gamefiles(self) -> bool:
        """
        Checks if the visual novel has a runscript and game files
        :return: The check result
        """
        runscript = os.path.join(self.metadata.directory_path, "run.sh")
        gamedir = os.path.join(self.metadata.directory_path, "game")
        valid = True

        if not os.path.isfile(runscript):
            valid = self.error("No runscript")
        if not os.path.isdir(gamedir):
            valid = self.error("No game directory")

        return valid

    def _check_extras(self) -> bool:
        """
        Makes sure that extras, like opening and ending theme videos are
        present, unless they've been explicitly excluded using the info.json
        file.
        :return: The check result
        """
        metadata = self.metadata  # type: VisualNovel  # type: ignore
        valid = True

        if metadata.has_op and metadata.ops is None:
            valid = self.warn("No Opening Video")
        if metadata.has_ed and metadata.eds is None:
            valid = self.warn("No Ending Video")
        if metadata.has_cgs and metadata.cgs is None:
            valid = self.warn("No CG Gallery")
        if metadata.has_ost and metadata.ost is None:
            valid = self.warn("No OST")

        return valid

    def _check_linux_drm_free_compatible(self) -> bool:
        """
        Checks whether or not the game is linux-compatible and DRM free.
        This is done by searching for a 'windows', 'steam', 'sony', or
        'nintendo' file in the game directory.
        If any of those are found, the game is deemed not DRM free and/or
        linux compatible
        :return: The check result
        """
        gamedir = os.path.join(self.metadata.directory_path, "game")
        for identifier in ["windows", "steam", "sony", "nintendo"]:
            if os.path.isfile(os.path.join(gamedir, identifier)):
                return self.warn("Not compatible with linux and DRM free: {}"
                                 .format(identifier))
        return True
