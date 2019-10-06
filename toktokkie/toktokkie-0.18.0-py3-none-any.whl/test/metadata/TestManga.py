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
from puffotter.os import listdir, create_file
from toktokkie.Directory import Directory
from toktokkie.metadata.Manga import Manga
from toktokkie.metadata.components.enums import IdType
from toktokkie.test.metadata.TestMetadata import _TestMetadata


class TestManga(_TestMetadata):
    """
    Class that tests the Manga metadata class
    """

    def test_renaming(self):
        """
        Tests renaming files associated with the metadata type
        :return: None
        """
        taisho = self.get("Taishou Otome Otogibanashi")
        taisho_dir = Directory(taisho)

        def check_files(correct: bool):
            """
            Checks that the files are named correctly
            :param correct: Whether or not the files should be named
                            correctly right now
            :return: None
            """
            meta = taisho_dir.metadata  # type: Manga

            for i, _ in enumerate(listdir(meta.main_path)):
                should = "{} - Chapter {}.cbz".format(
                    meta.name,
                    str(i + 1).zfill(2)
                )

                dest = os.path.join(meta.main_path, should)
                self.assertEqual(correct, os.path.isfile(dest))
            for chap in meta.special_chapters:
                should = "{} - Chapter {}.cbz".format(
                    meta.name,
                    chap.zfill(4)
                )
                dest = os.path.join(meta.special_path, should)
                self.assertEqual(correct, os.path.isfile(dest))

        metadata = taisho_dir.metadata  # type: Manga

        for chapter, path in listdir(metadata.main_path):
            os.rename(
                path,
                os.path.join(metadata.main_path, "A" + chapter)
            )
        for chapter, path in listdir(metadata.special_path):
            os.rename(
                path,
                os.path.join(metadata.special_path, "B" + chapter)
            )

        check_files(False)
        taisho_dir.rename(noconfirm=True)
        check_files(True)

        taisho_dir.metadata.set_ids(IdType.ANILIST, [106988])
        taisho_dir.rename(noconfirm=True)

        self.assertEqual(taisho_dir.metadata.name, "Shouwa Otome Otogibanashi")
        check_files(True)

    def test_prompt(self):
        """
        Tests generating a new metadata object using user prompts
        :return: None
        """
        showa = self.get("Shouwa Otome Otogibanashi")
        os.makedirs(showa)
        os.makedirs(os.path.join(showa, "Special"))
        create_file(os.path.join(showa, "Special/Chap 5.5.cbz"))
        with mock.patch("builtins.input", side_effect=[
            "shouwa, romance, sequel", "", "", "106988", "", "", "5.5"
        ]):
            metadata = Manga.prompt(showa)
            metadata.write()

        directory = Directory(showa)

        self.assertTrue(os.path.isdir(directory.meta_dir))
        self.assertTrue(os.path.isfile(metadata.metadata_file))
        self.assertEqual(metadata, directory.metadata)
        self.assertEqual(metadata.ids[IdType.ANILIST], ["106988"])
        self.assertEqual(metadata.ids[IdType.MYANIMELIST], [])
        self.assertEqual(metadata.ids[IdType.KITSU], [])
        self.assertEqual(metadata.ids[IdType.MANGADEX], [])
        self.assertEqual(metadata.ids[IdType.ISBN], [])
        self.assertEqual(metadata.special_chapters, ["5.5"])

        for invalid in [IdType.VNDB, IdType.IMDB, IdType.TVDB]:
            self.assertFalse(invalid in metadata.ids)

        for tag in ["shouwa", "romance", "sequel"]:
            self.assertTrue(tag in metadata.tags)

        special_file = os.path.join(
            showa, "Special/Shouwa Otome Otogibanashi - Chapter 5.5.cbz"
        )
        self.assertFalse(os.path.isfile(special_file))
        directory.rename(noconfirm=True)
        self.assertTrue(os.path.isfile(special_file))

    def test_validation(self):
        """
        Tests if the validation of metadata works correctly
        :return: None
        """
        valid_data = [
            {"type": "manga", "ids": {"anilist": ["106988"]}},
            {"type": "manga", "ids": {"anilist": "106988"}},
        ]
        invalid_data = [
            {},
            {"type": "manga"},
            {"type": "manga", "ids": {}},
            {"type": "manga", "ids": {"anilist": 1}},
            {"type": "manga", "ids": {"anilist": [1]}},
            {"type": "manga", "ids": {"tvdb": ["106988"]}},
            {"type": "tv_series", "ids": {"anilist": ["106988"]}}
        ]
        taisho = self.get("Taishou Otome Otogibanashi")
        self.check_validation(valid_data, invalid_data, Manga, taisho)

    def test_checking(self):
        """
        Tests if the checking mechanisms work correctly
        :return: None
        """
        taisho = Directory(self.get("Taishou Otome Otogibanashi"))
        self.assertTrue(taisho.check(False, False, {}))

        icon = os.path.join(taisho.meta_dir, "icons/main.png")
        os.remove(icon)
        self.assertFalse(taisho.check(False, False, {}))
        create_file(icon)
        self.assertTrue(taisho.check(False, False, {}))

        chapter_one = os.path.join(
            taisho.metadata.main_path,
            "Taishou Otome Otogibanashi - Chapter 01.cbz"
        )
        os.remove(chapter_one)
        self.assertFalse(taisho.check(False, False, {}))
        create_file(chapter_one)
        self.assertTrue(taisho.check(False, False, {}))

        chapter_eightfive = os.path.join(
            taisho.metadata.special_path,
            "Taishou Otome Otogibanashi - Chapter 08.5.cbz"
        )
        os.remove(chapter_eightfive)
        self.assertFalse(taisho.check(False, False, {}))
        create_file(chapter_eightfive)
        self.assertTrue(taisho.check(False, False, {}))
