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

from enum import Enum
from typing import Dict, Any, List
from toktokkie.metadata.Metadata import Metadata
from toktokkie.metadata.components.enums import IdType
from toktokkie.exceptions import InvalidMetadata


class MetadataPart:
    """
    Class that defines various functionality of a metadata part
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
        self.validate()

    def validate(self):
        """
        Validates the JSON data of the metadata part
        :return: None
        :raises InvalidMetadataException: If something is wrong
                                          with the JSON data
        """
        if len(self.ids) < 1:
            raise InvalidMetadata()
        for _, ids in self.ids.items():
            for _id in ids:
                if not type(_id) == str:
                    print(type(_id))
                    print("AAAAAAAAAAAAAAAAAA")
                    raise InvalidMetadata()

    @property
    def ids(self) -> Dict[IdType, List[str]]:
        """
        :return: A dictionary containing lists of IDs mapped to ID types
        """
        generated = self.parent.ids
        for id_type, _id in self.json.get("ids", {}).items():
            if isinstance(_id, list):
                generated[IdType(id_type)] = _id
            else:
                generated[IdType(id_type)] = [_id]
        return generated

    @ids.setter
    def ids(self, ids: Dict[IdType, List[str]]):
        """
        Setter method for the IDs of the metadata part object.
        Previous IDs will be overwritten!
        :param ids: The IDs to set
        :return: None
        """
        self.json["ids"] = {}
        for id_type, values in ids.items():
            self.json["ids"][id_type.value] = values
