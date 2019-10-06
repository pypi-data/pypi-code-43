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
from typing import Dict, Any
from toktokkie.exceptions import InvalidMetadata
from toktokkie.metadata.components.enums import IdType
from toktokkie.metadata.Metadata import Metadata
from toktokkie.metadata.components.MetadataPart import MetadataPart


class TvSeason(MetadataPart):
    """
    Class that models a single tv season
    """

    def __init__(self, parent: Metadata, json_data: Dict[str, Any]):
        """
        Initializes the MetadataPart object using JSON data
        :param parent: The parent metadata
        :param json_data: The JSON data used to generate the MetadataPart
        :raises InvalidMetadataException: If any errors were encountered
                                          while generating the object
        """
        self.parent = parent
        self.json = json_data
        super().__init__(parent, json_data)

    @property
    def name(self) -> str:
        """
        :return: The name of the season directory
        """
        return self.json["name"]

    @property
    def path(self) -> str:
        """
        :return: The path to the season directory
        """
        return os.path.join(self.parent.directory_path, self.name)

    @property
    def tvdb_id(self) -> str:
        """
        :return: The TVDB ID of the TV season
        """
        return self.ids[IdType.TVDB][0]

    @property
    def season_number(self) -> int:
        """
        :return: The season number of the season
        """
        if self.name.lower().startswith("season "):
            return int(self.name.lower().split("season")[1])
        else:
            return 0

    def validate(self):
        """
        Validates the JSON data of the tv season.
        :return: None
        :raises InvalidMetadataException: If something is wrong
                                          with the JSON data
        """
        super().validate()

        if not os.path.exists(self.path) or "name" not in self.json:
            raise InvalidMetadata()

        if not os.path.isdir(self.path):
            raise InvalidMetadata()
        try:
            if not self.tvdb_id == self.ids[IdType.TVDB][0]:
                raise InvalidMetadata()
        except (KeyError, IndexError):
            raise InvalidMetadata("Missing TVDB ID")

    def is_spinoff(self) -> bool:
        """
        :return: Whether or not this season is a spinoff
        """
        # noinspection PyUnresolvedReferences
        return self.parent.tvdb_id != self.tvdb_id  # type: ignore
