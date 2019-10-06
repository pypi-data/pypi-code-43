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
from typing import Optional, List, Dict, Any
from puffotter.os import listdir
from toktokkie.metadata.Metadata import Metadata
from toktokkie.metadata.components.enums import MediaType


class VisualNovel(Metadata):
    """
    Metadata class that model a visual novel
    """

    @classmethod
    def media_type(cls) -> MediaType:
        """
        :return: The media type of the Metadata class
        """
        return MediaType.VISUAL_NOVEL

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

    @property
    def has_ed(self) -> bool:
        """
        :return: Whether or not the Visual Novel has an ending theme
        """
        return self.json.get("has_ed", True)

    @has_ed.setter
    def has_ed(self, has_ed: bool):
        """
        Setter method for the has_ed property
        :param has_ed: Whether or not the VN has an ending theme
        :return: None
        """
        self.json["has_ed"] = has_ed

    @property
    def has_op(self) -> bool:
        """
        :return: Whether or not the Visual Novel has an opening theme
        """
        return self.json.get("has_op", True)

    @has_op.setter
    def has_op(self, has_op: bool):
        """
        Setter method for the has_op property
        :param has_op: Whether or not the VN has an opening theme
        :return: None
        """
        self.json["has_op"] = has_op

    @property
    def has_cgs(self) -> bool:
        """
        :return: Whether or not the Visual Novel has a CG gallery
        """
        return self.json.get("has_cgs", True)

    @has_cgs.setter
    def has_cgs(self, has_cgs: bool):
        """
        Setter method for the has_cgs property
        :param has_cgs: Whether or not the VN has a CG gallery
        :return: None
        """
        self.json["has_cgs"] = has_cgs

    @property
    def has_ost(self) -> bool:
        """
        :return: Whether or not the Visual Novel has an OST
        """
        return self.json.get("has_ost", True)

    @has_ost.setter
    def has_ost(self, has_ost: bool):
        """
        Setter method for the has_ost property
        :param has_ost: Whether or not the VN has an OST
        :return: None
        """
        self.json["has_ost"] = has_ost

    @property
    def cgs(self) -> Optional[Dict[str, str]]:
        """
        Generates a dictionary of paths to CG images
        :return: A dictionary mapping the various CG images to their
                 respective directory identifiers
        """

        cg_dirs = os.path.join(self.directory_path, ".meta/cgs")
        if not os.path.isdir(cg_dirs):
            return None
        else:
            cgs = {}
            for cg_dir, cg_dir_path in listdir(cg_dirs, no_files=True):
                for _, img_path in listdir(cg_dir_path, no_dirs=True):
                    cgs[cg_dir] = img_path
            if len(cgs) == 0:
                return None
            else:
                return cgs

    @property
    def ost(self) -> Optional[List[str]]:
        """
        :return: a list of files for the OST of a visual novel
        """
        ost_dir = os.path.join(self.directory_path, ".meta/ost")
        return self._get_file_list(ost_dir)

    @property
    def eds(self) -> Optional[List[str]]:
        """
        :return: a list of ending theme videos
        """
        video_dir = os.path.join(self.directory_path, ".meta/videos")
        return self._get_file_list(video_dir, "ED")

    @property
    def ops(self) -> Optional[List[str]]:
        """
        :return: a list of opening theme videos
        """
        video_dir = os.path.join(self.directory_path, ".meta/videos")
        return self._get_file_list(video_dir, "OP")

    @staticmethod
    def _get_file_list(path: str, prefix: Optional[str] = None) \
            -> Optional[List[str]]:
        """
        Retrieves a list of files from a directory
        :param path: The path to check
        :param prefix: An optional prefix
        :return: None, if no files were found or the directory does not exist,
                 otherwise the list of files
        """
        if not os.path.isdir(path):
            return None
        else:
            files = []
            for _file, file_path in listdir(path, no_dirs=True):
                if prefix is not None and not _file.startswith(prefix):
                    continue
                files.append(file_path)
            if len(files) == 0:
                return None
            else:
                return files

    def _validate_json(self):
        """
        Validates the JSON data to make sure everything has valid values
        :raises InvalidMetadataException: If any errors were encountered
        :return: None
        """
        pass
