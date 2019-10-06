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
from typing import List, Dict, Any
from toktokkie.metadata.Metadata import Metadata
from toktokkie.metadata.components.enums import MediaType
from puffotter.prompt import prompt_comma_list


class Manga(Metadata):
    """
    Metadata class that models a Manga series
    """

    @classmethod
    def media_type(cls) -> MediaType:
        """
        :return: The media type of the Metadata class
        """
        return MediaType.MANGA

    @classmethod
    def _prompt(cls, directory_path: str, json_data: Dict[str, Any]) \
            -> Dict[str, Any]:
        """
        Prompts the user for metadata-type-specific information
        Should be extended by child classes
        :param directory_path: The path to the directory for which to generate
                               the metadata
        :param json_data: Previously generated JSON data
        :return: The generated metadata JSON data
        """
        json_data["special_chapters"] = []
        series = Manga(directory_path, json_data)

        if not os.path.isdir(series.main_path):
            os.makedirs(series.main_path)

        if os.path.isdir(series.special_path):
            print("Please enter identifiers for special chapters:")
            for _file in sorted(os.listdir(series.special_path)):
                print(_file)
            series.special_chapters = prompt_comma_list("Special Chapters")

        return series.json

    @property
    def main_path(self) -> str:
        """
        The path to the main manga directory
        :return: The path
        """
        return os.path.join(self.directory_path, "Main")

    @property
    def special_path(self) -> str:
        """
        The path to the special manga directory
        :return: The path or None if it does not exist
        """
        return os.path.join(self.directory_path, "Special")

    @property
    def special_chapters(self) -> List[str]:
        """
        :return: A list of special chapter identifiers for this series
        """
        return self.json.get("special_chapters", [])

    @special_chapters.setter
    def special_chapters(self, special_chapters: List[str]):
        """
        Setter method for the special_chapters
        :param special_chapters: The special chapter identifiers to set
        :return: None
        """
        max_len = len(max(special_chapters, key=lambda x: len(x)))
        special_chapters.sort(key=lambda x: x.zfill(max_len))
        self.json["special_chapters"] = special_chapters

    def _validate_json(self):
        """
        Validates the JSON data to make sure everything has valid values
        :raises InvalidMetadataException: If any errors were encountered
        :return: None
        """
        pass
