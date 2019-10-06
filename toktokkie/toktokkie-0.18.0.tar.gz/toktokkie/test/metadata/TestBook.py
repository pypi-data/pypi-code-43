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
from toktokkie.test.metadata.TestMetadata import _TestMetadata
from toktokkie.metadata.Book import Book
from toktokkie.metadata.components.enums import IdType


class TestBook(_TestMetadata):
    """
    Class that tests the Book metadata class
    """

    def test_renaming(self):
        """
        Tests renaming files associated with the metadata type
        :return: None
        """
        faust = self.get("Faust")
        correct = os.path.join(faust, "Faust.txt")
        incorrect = os.path.join(faust, "Fausti.txt")
        os.rename(correct, incorrect)

        self.assertFalse(os.path.isfile(correct))
        self.assertTrue(os.path.isfile(incorrect))

        faust_dir = Directory(faust)
        faust_dir.rename(noconfirm=True)

        self.assertTrue(os.path.isfile(correct))
        self.assertFalse(os.path.isfile(incorrect))

        faust_dir.metadata.set_ids(IdType.ANILIST, [39115])
        faust_dir.rename(noconfirm=True)

        self.assertEqual(faust_dir.metadata.name, "Spice & Wolf")
        self.assertFalse(os.path.isfile(correct))
        self.assertTrue(os.path.isfile(
            self.get("Spice & Wolf/Spice & Wolf.txt")
        ))

    def test_prompt(self):
        """
        Tests generating a new metadata object using user prompts
        :return: None
        """
        faust_two = self.get("Faust 2")
        os.makedirs(faust_two)
        with mock.patch("builtins.input", side_effect=[
            "school, faust, goethe", "1502597918", "", "", ""
        ]):
            metadata = Book.prompt(faust_two)
            metadata.write()

        directory = Directory(faust_two)

        self.assertTrue(os.path.isdir(directory.meta_dir))
        self.assertTrue(os.path.isfile(metadata.metadata_file))
        self.assertEqual(metadata, directory.metadata)
        self.assertEqual(metadata.ids[IdType.ISBN], ["1502597918"])
        self.assertEqual(metadata.ids[IdType.ANILIST], [])
        self.assertEqual(metadata.ids[IdType.MYANIMELIST], [])
        self.assertEqual(metadata.ids[IdType.KITSU], [])

        for invalid in [IdType.VNDB, IdType.MANGADEX, IdType.TVDB]:
            self.assertFalse(invalid in metadata.ids)

        for tag in ["school", "faust", "goethe"]:
            self.assertTrue(tag in metadata.tags)

    def test_validation(self):
        """
        Tests if the validation of metadata works correctly
        :return: None
        """
        valid_data = [
            {"type": "book", "ids": {"isbn": ["100"]}},
            {"type": "book", "ids": {"isbn": "100"}}
        ]
        invalid_data = [
            {},
            {"type": "book"},
            {"type": "book", "ids": {}},
            {"type": "book", "ids": {"isbn": 100}},
            {"type": "book", "ids": {"isbn": [100]}},
            {"type": "movie", "ids": {"isbn": ["100"]}}
        ]
        faust = self.get("Faust")
        self.check_validation(valid_data, invalid_data, Book, faust)

    def test_checking(self):
        """
        Tests if the checking mechanisms work correctly
        :return: None
        """
        faust = Directory(self.get("Faust"))
        self.assertTrue(faust.check(False, False, {}))
        os.remove(os.path.join(faust.meta_dir, "icons/main.png"))
        self.assertFalse(faust.check(False, False, {}))
