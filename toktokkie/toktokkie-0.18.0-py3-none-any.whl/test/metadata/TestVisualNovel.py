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
from unittest import mock
from toktokkie.Directory import Directory
from toktokkie.metadata.VisualNovel import VisualNovel
from toktokkie.metadata.components.enums import IdType
from toktokkie.test.metadata.TestMetadata import _TestMetadata


class TestVisualNovel(_TestMetadata):
    """
    Class that tests the VisualNovel metadata class
    """

    def test_renaming(self):
        """
        Tests renaming files associated with the metadata type
        :return: None
        """
        pass  # Currently no renaming functionality implemented

    def test_prompt(self):
        """
        Tests generating a new metadata object using user prompts
        :return: None
        """
        evangile = self.get("Princess Evangile")
        os.makedirs(evangile)

        with mock.patch("builtins.input", side_effect=[
            "moege, school", "v6710"
        ]):
            metadata = VisualNovel.prompt(evangile)
            metadata.write()

        directory = Directory(evangile)

        self.assertTrue(os.path.isdir(directory.meta_dir))
        self.assertTrue(os.path.isfile(metadata.metadata_file))
        self.assertEqual(metadata, directory.metadata)
        self.assertEqual(metadata.ids[IdType.VNDB], ["v6710"])

        for id_type in IdType:
            if id_type not in [IdType.VNDB]:
                self.assertFalse(id_type in metadata.ids)

        for tag in ["school", "moege"]:
            self.assertTrue(tag in metadata.tags)

    def test_validation(self):
        """
        Tests if the validation of metadata works correctly
        :return: None
        """
        valid_data = [
            {"type": "visual_novel", "ids": {"vndb": ["v6710"]}},
            {"type": "visual_novel", "ids": {"vndb": "v6710"}}
        ]
        invalid_data = [
            {},
            {"type": "visual_novel"},
            {"type": "visual_novel", "ids": {}},
            {"type": "visual_novel", "ids": {"tvdb": ["6710"]}},
            {"type": "visual_novel", "ids": {"vndb": [6710]}},
            {"type": "visual_novel", "ids": {"vndb": 6710}},
            {"type": "book", "ids": {"vndb": ["v6710"]}}
        ]
        fureraba = self.get("Fureraba")
        self.check_validation(valid_data, invalid_data, VisualNovel, fureraba)

    def test_checking(self):
        """
        Tests if the checking mechanisms work correctly
        :return: None
        """
        fureraba = Directory(self.get("Fureraba"))
        self.assertTrue(fureraba.check(False, False, {}))
        os.remove(os.path.join(fureraba.meta_dir, "icons/main.png"))
        self.assertFalse(fureraba.check(False, False, {}))
