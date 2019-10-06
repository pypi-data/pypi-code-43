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

from typing import Dict, Any
from toktokkie.metadata.Metadata import Metadata
from toktokkie.metadata.components.enums import MediaType


class Movie(Metadata):
    """
    Metadata class that model a Movie
    """

    @classmethod
    def media_type(cls) -> MediaType:
        """
        :return: The media type of the Metadata class
        """
        return MediaType.MOVIE

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
        return {}

    def _validate_json(self):
        """
        Validates the JSON data to make sure everything has valid values
        :raises InvalidMetadataException: If any errors were encountered
        :return: None
        """
        pass
