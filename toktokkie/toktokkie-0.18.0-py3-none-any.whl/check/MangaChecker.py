"""
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
"""

import os
import json
import requests
from typing import Optional, List
from toktokkie.check.Checker import Checker
from toktokkie.metadata.Manga import Manga
from toktokkie.metadata.components.enums import IdType
from anime_list_apis.api.AnilistApi import AnilistApi
from anime_list_apis.models.MediaListEntry import MangaListEntry
from anime_list_apis.models.attributes.Id import IdType as AnimeListIdType


class MangaChecker(Checker):
    """
    Class that check Manga media for consistency
    """

    def check(self) -> bool:
        """
        Performs sanity checks and prints out anything that's wrong
        :return: The result of the check
        """
        valid = super().check()
        valid = self._check_special_chapter_count() and valid
        if self.config.get("anilist_user") is not None:
            valid = self._check_chapter_progress() and valid
        return valid

    def _check_icons(self) -> bool:
        """
        Only checks for a main.png icon file.
        :return: The result of the check
        """
        valid = True

        if not os.path.isdir(self.metadata.icon_directory):
            valid = self.error("Missing icon directory")

        main_icon = os.path.join(self.metadata.icon_directory, "main.png")
        if not os.path.isfile(main_icon):
            valid = self.error("Missing main icon file for {}".format(
                self.metadata.name
            ))

        return valid

    def _check_special_chapter_count(self) -> bool:
        """
        Checks if the correct amount of special chapters exist in the special
        directory
        :return: True if correct, False otherwise
        """
        # noinspection PyTypeChecker
        metadata = self.metadata  # type: Manga  # type: ignore

        should = len(os.listdir(metadata.special_path))
        _is = len(metadata.special_chapters)
        if should != _is:
            self.error(
                "Incorrect amount of special chapters: Should: {}, Is: {}"
                .format(should, _is)
            )
            return False
        return True

    def _check_chapter_progress(self) -> bool:
        """
        Checks the chapter progress using the best guess anilist user data
        can give us.
        :return: The result of the check
        """
        # noinspection PyTypeChecker
        metadata = self.metadata  # type: Manga  # type: ignore
        anilist_entries = self.config["anilist_manga_list"]

        local_chaptercount = len(os.listdir(metadata.main_path))

        try:
            anilist_ids = metadata.ids.get(IdType.ANILIST)
            if anilist_ids is None:
                raise IndexError
            anilist_id = int(anilist_ids[0])

            list_entry = None
            for entry in anilist_entries:  # type: MangaListEntry
                if entry.id.get(AnimeListIdType.ANILIST) == anilist_id:
                    list_entry = entry
                    break

            list_chaptercount = None
            if list_entry is not None:
                list_chaptercount = list_entry.chapter_progress

            remote_chaptercount = self._guess_latest_chapter(int(anilist_id))

            list_complete = list_chaptercount == local_chaptercount
            remote_complete = remote_chaptercount == local_chaptercount

            if not list_complete:
                self.warn("Local chapters and list chapters "
                          "don't match: Local: {} / List: {}"
                          .format(local_chaptercount, list_chaptercount))

            if not remote_complete:
                self.warn("Local chapters and available chapters "
                          "don't match: Local: {} / Available: {}"
                          .format(local_chaptercount, remote_chaptercount))

            return list_complete and remote_complete

        except (IndexError, ValueError):
            self.warn("No Anilist ID for {}".format(metadata.name))
            return True

    def _guess_latest_chapter(self, anilist_id: int) -> Optional[int]:
        """
        Guesses the latest chapter number based on anilist user activity
        :param anilist_id: The anilist ID to check
        :return: The latest chapter number
        """
        api = self.config["anilist_api"]  # type: AnilistApi
        info = api.get_manga_data(anilist_id)

        chapter_count = info.chapter_count
        if chapter_count is None:  # Guess if not official data is present
            query = """
            query ($id: Int) {
              Page(page: 1) {
                activities(mediaId: $id, sort: ID_DESC) {
                  ... on ListActivity {
                    progress
                    userId
                  }
                }
              }
            }
            """
            resp = requests.post(
                "https://graphql.anilist.co",
                json={"query": query, "variables": {"id": anilist_id}}
            )
            data = json.loads(resp.text)["data"]["Page"]["activities"]

            progresses = []
            for entry in data:
                progress = entry["progress"]
                if progress is not None:
                    progress = entry["progress"].split(" - ")[-1]
                    progresses.append(int(progress))

            progresses.sort()
            chapter_count = progresses[-1]

        return chapter_count
