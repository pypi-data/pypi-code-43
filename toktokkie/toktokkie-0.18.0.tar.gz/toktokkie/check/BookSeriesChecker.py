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

from toktokkie.check.Checker import Checker
from toktokkie.metadata.BookSeries import BookSeries
from toktokkie.metadata.components.enums import IdType
from anime_list_apis.models.attributes.Id import IdType as AnimeListIdType


class BookSeriesChecker(Checker):
    """
    Class that check Book Series media for consistency
    """

    def check(self) -> bool:
        """
        Performs sanity checks and prints out anything that's wrong
        :return: The result of the check
        """
        valid = super().check()
        if self.config.get("anilist_user") is not None:
            valid = self._check_anilist_read_state() and valid
        return valid

    def _check_anilist_read_state(self) -> bool:
        """
        Checks if the anilist user is up-to-date with all available volumes
        :return: The check result
        """
        metadata = self.metadata  # type: BookSeries  # type: ignore
        manga_list = self.config["anilist_manga_list"]

        try:
            _id = metadata.ids.get(IdType.ANILIST, [])[0]
        except IndexError:
            return self.error("No Anilist ID")

        anilist_id = int(_id)
        manga = None
        for entry in manga_list:
            if entry.id.get(AnimeListIdType.ANILIST) == anilist_id:
                manga = entry
                break

        if manga is None:
            return self.error("Not in Anilist")
        else:
            volumes_local = len(metadata.volumes)
            volumes_read = manga.volume_progress
            if volumes_read < volumes_local:
                return self.warn("User has only read {}/{} volumes".format(
                    volumes_read, volumes_local
                ))
            elif volumes_local < volumes_read:
                return self.warn(
                    "Some read volumes do not exist locally "
                    "(Read:{}, Local:{})".format(
                        volumes_read, volumes_local
                    ))
            else:
                return True
