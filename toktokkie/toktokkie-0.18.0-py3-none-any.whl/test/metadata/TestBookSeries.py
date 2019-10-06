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
from toktokkie.metadata.components.enums import IdType
from toktokkie.metadata.BookSeries import BookSeries
from toktokkie.test.metadata.TestMetadata import _TestMetadata
from puffotter.os import listdir, create_file


class TestBookSeries(_TestMetadata):
    """
    Class that tests the BookSeries metadata class
    """

    def test_renaming(self):
        """
        Tests renaming files associated with the metadata type
        :return: None
        """
        bsb = self.get("Bluesteel Blasphemer")
        bsb_dir = Directory(bsb)

        correct_files = []
        incorrect_files = []
        for volume, path in listdir(bsb):

            new_file = os.path.join(bsb, "AAA" + volume)
            os.rename(path, new_file)

            correct_files.append(path)
            incorrect_files.append(new_file)
            self.assertFalse(os.path.isfile(path))
            self.assertTrue(os.path.isfile(new_file))

        bsb_dir.rename(noconfirm=True)

        for correct_file in correct_files:
            self.assertTrue(os.path.isfile(correct_file))
        for incorrect_file in incorrect_files:
            self.assertFalse(os.path.isfile(incorrect_file))

        bsb_dir.metadata.name = "Not Bluesteel Blasphemer"
        with mock.patch("builtins.input", side_effect=[
            "n", "y"
        ]):
            bsb_dir.rename()

        self.assertTrue(os.path.isdir(self.get("Not Bluesteel Blasphemer")))
        self.assertFalse(os.path.isdir(bsb))

        for correct_file in correct_files:
            self.assertFalse(os.path.isfile(correct_file))
            self.assertTrue(os.path.isfile(correct_file.replace(
                "Bluesteel Blasphemer", "Not Bluesteel Blasphemer"
            )))

        bsb_dir.rename(noconfirm=True)

        for correct_file in correct_files:
            self.assertTrue(os.path.isfile(correct_file))
            self.assertFalse(os.path.isfile(correct_file.replace(
                "Bluesteel Blasphemer", "Not Bluesteel Blasphemer"
            )))

    def test_prompt(self):
        """
        Tests generating a new metadata object using user prompts
        :return: None
        """
        sp_n_wo = self.get("Spice & Wolf")
        os.makedirs(sp_n_wo)
        create_file(os.path.join(sp_n_wo, "Volume 1.epub"))
        create_file(os.path.join(sp_n_wo, "Volume 2.epub"))

        with mock.patch("builtins.input", side_effect=[
            "anime, holo",
            "", "9115", "", "",
            "ABC", "", "", "",
            "", "", "100685", "1"
        ]):
            metadata = BookSeries.prompt(sp_n_wo)
            metadata.write()

        directory = Directory(sp_n_wo)
        directory.rename(noconfirm=True)

        self.assertTrue(os.path.isfile(metadata.metadata_file))
        self.assertEqual(metadata, directory.metadata)
        self.assertEqual(metadata.ids[IdType.ISBN], [])
        self.assertEqual(metadata.ids[IdType.ANILIST], ["39115"])
        self.assertEqual(metadata.ids[IdType.MYANIMELIST], ["9115"])
        self.assertEqual(metadata.ids[IdType.KITSU], [])
        self.assertEqual(metadata.volumes[1].ids[IdType.ISBN], ["ABC"])
        self.assertEqual(metadata.volumes[1].ids[IdType.ANILIST], ["39115"])
        self.assertEqual(metadata.volumes[1].ids[IdType.MYANIMELIST], ["9115"])
        self.assertEqual(metadata.volumes[1].ids[IdType.KITSU], [])
        self.assertEqual(metadata.volumes[2].ids[IdType.ISBN], [])
        self.assertEqual(metadata.volumes[2].ids[IdType.ANILIST], ["100685"])
        self.assertEqual(metadata.volumes[2].ids[IdType.MYANIMELIST], ["9115"])
        self.assertEqual(metadata.volumes[2].ids[IdType.KITSU], ["1"])

        for invalid in [IdType.VNDB, IdType.MANGADEX, IdType.TVDB]:
            self.assertFalse(invalid in metadata.ids)
            for _, volume in metadata.volumes.items():
                self.assertFalse(invalid in volume.ids)

        for tag in ["anime", "holo"]:
            self.assertTrue(tag in metadata.tags)

    def test_validation(self):
        """
        Tests if the validation of metadata works correctly
        :return: None
        """
        valid_data = [
            {"type": "book_series", "ids": {"isbn": ["100"]}, "volumes": {}},
            {"type": "book_series", "ids": {"isbn": "100"}, "volumes": {}},
            {"type": "book_series", "ids": {"isbn": ["100"]}, "volumes": {
                "ids": {"isbn": ["1000"]}
            }},
        ]
        invalid_data = [
            {},
            {"type": "book_series", "ids": {"isbn": 100}, "volumes": {}},
            {"type": "book_series", "volumes": {}},
            {"type": "book_series", "ids": {}},
            {"type": "movie", "ids": {"isbn": ["100"]}, "volumes": {}},
            {"type": "book_series", "ids": {"isbn": ["100"]}, "volumes": {
                "1": {"ids": {"isbn": 1000}}
            }},
        ]
        bsb = self.get("Bluesteel Blasphemer")
        self.check_validation(valid_data, invalid_data, BookSeries, bsb)

    def test_checking(self):
        """
        Tests if the checking mechanisms work correctly
        :return: None
        """
        bsb = Directory(self.get("Bluesteel Blasphemer"))
        self.assertTrue(bsb.check(False, False, {}))

        icon = os.path.join(bsb.meta_dir, "icons/main.png")
        os.remove(icon)
        self.assertFalse(bsb.check(False, False, {}))
        create_file(icon)
        self.assertTrue(bsb.check(False, False, {}))

        for volume, path in listdir(bsb.path, no_dirs=True):
            os.rename(path, os.path.join(bsb.path, "AAA" + volume))
        self.assertFalse(bsb.check(False, False, {}))
        bsb.rename(noconfirm=True)
        self.assertTrue(bsb.check(False, False, {}))
