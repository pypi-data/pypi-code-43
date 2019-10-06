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
from unittest import mock
from puffotter.os import listdir
from toktokkie.Directory import Directory
from toktokkie.metadata.TvSeries import TvSeries
from toktokkie.metadata.components.enums import IdType
from toktokkie.test.metadata.TestMetadata import _TestMetadata


class TestTvSeries(_TestMetadata):
    """
    Test class for TV metadata
    """

    def test_renaming(self):
        """
        Tests renaming files associated with the metadata type
        :return: None
        """
        otgw = self.get("Over the Garden Wall")
        otgw_dir = Directory(otgw)
        otgw_dir.rename(noconfirm=True)

        correct = []
        wrong = []
        for _, season_dir in listdir(otgw):
            for episode, episode_file in listdir(season_dir):
                new_file = os.path.join(season_dir, "A" + episode)
                os.rename(episode_file, new_file)
                correct.append(episode_file)
                wrong.append(new_file)

        for _file in correct:
            self.assertFalse(os.path.isfile(_file))
        for _file in wrong:
            self.assertTrue(os.path.isfile(_file))

        otgw_dir.rename(noconfirm=True)

        for _file in correct:
            self.assertTrue(os.path.isfile(_file))
        for _file in wrong:
            self.assertFalse(os.path.isfile(_file))

        otgw_dir.metadata.set_ids(IdType.ANILIST, ["19815"])
        otgw_dir.rename(noconfirm=True)

        self.assertEqual(otgw_dir.metadata.name, "No Game No Life")

        for _file in correct:
            self.assertFalse(os.path.isfile(_file))

    def test_prompt(self):
        """
        Tests generating a new metadata object using user prompts
        :return: None
        """
        ngnl = self.get("No Game No Life")
        os.makedirs(ngnl)
        os.makedirs(os.path.join(ngnl, "Season 1"))
        os.makedirs(os.path.join(ngnl, "Movie"))
        with mock.patch("builtins.input", side_effect=[
            "anime, no_second_season", "278155", "19815", "", "",
            "", "", "", "",
            "", "33674", "", ""
        ]):
            metadata = TvSeries.prompt(ngnl)
            metadata.write()

        directory = Directory(ngnl)

        self.assertTrue(os.path.isdir(directory.meta_dir))
        self.assertTrue(os.path.isfile(metadata.metadata_file))
        self.assertEqual(metadata, directory.metadata)
        self.assertEqual(metadata.ids[IdType.TVDB], ["278155"])
        self.assertEqual(metadata.ids[IdType.ANILIST], ["19815"])
        self.assertEqual(metadata.ids[IdType.MYANIMELIST], ["19815"])
        self.assertEqual(metadata.ids[IdType.KITSU], [])

        season_one = metadata.get_season("Season 1")
        movie = metadata.get_season("Movie")

        self.assertEqual(season_one.ids[IdType.TVDB], ["278155"])
        self.assertEqual(season_one.ids[IdType.ANILIST], ["19815"])
        self.assertEqual(season_one.ids[IdType.MYANIMELIST], ["19815"])
        self.assertEqual(season_one.ids[IdType.KITSU], [])
        self.assertEqual(movie.ids[IdType.TVDB], ["278155"])
        self.assertEqual(movie.ids[IdType.ANILIST], ["21875"])
        self.assertEqual(movie.ids[IdType.MYANIMELIST], ["33674"])
        self.assertEqual(movie.ids[IdType.KITSU], [])

        for invalid in [
            IdType.VNDB, IdType.MANGADEX, IdType.IMDB, IdType.ISBN
        ]:
            self.assertFalse(invalid in metadata.ids)

        for tag in ["anime", "no_second_season"]:
            self.assertTrue(tag in metadata.tags)

    def test_validation(self):
        """
        Tests if the validation of metadata works correctly
        :return: None
        """
        valid_data = [
            {"type": "tv", "ids": {"tvdb": ["281643"]},
             "seasons": [{"name": "Season 1", "ids": {}}]},
            {"type": "tv", "ids": {"tvdb": "281643"},
             "seasons": [{"name": "Season 1", "ids": {}}]},
        ]
        invalid_data = [
            {},
            {"type": "tv", "ids": {"tvdb": ["281643"]},
             "seasons": [{"name": "Season 2", "ids": {}}]},
            {"type": "tv", "ids": {"tvdb": ["281643"]},
             "seasons": []},
            {"type": "tv", "ids": {"tvdb": ["281643"]}},
            {"type": "tv", "seasons": [{"name": "Season 1", "ids": {}}]},
            {"type": "movie", "ids": {"tvdb": ["281643"]},
             "seasons": [{"name": "Season 1", "ids": {}}]},
            {"type": "tv", "ids": {"tvdb": 281643},
             "seasons": [{"name": "Season 1", "ids": {}}]},
            {"type": "tv", "ids": {"tvdb": [281643]},
             "seasons": [{"name": "Season 1", "ids": {}}]},
            {"type": "tv", "ids": {"isbn": ["281643"]},
             "seasons": [{"name": "Season 1", "ids": {}}]},
        ]
        otgw = self.get("Over the Garden Wall")
        self.check_validation(valid_data, invalid_data, TvSeries, otgw)

    def test_checking(self):
        """
        Tests if the checking mechanisms work correctly
        :return: None
        """
        otgw = Directory(self.get("Over the Garden Wall"))
        self.assertTrue(otgw.check(False, False, {}))
        os.remove(os.path.join(otgw.meta_dir, "icons/main.png"))
        self.assertFalse(otgw.check(False, False, {}))
