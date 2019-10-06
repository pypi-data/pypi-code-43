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
from tvdb_api import tvdb_shownotfound
from typing import Dict, Optional, List
from datetime import datetime
from colorama import Fore, Style
from toktokkie.check.Checker import Checker
from toktokkie.renaming.Renamer import Renamer
from toktokkie.renaming.RenameOperation import RenameOperation
from toktokkie.metadata.TvSeries import TvSeries
from toktokkie.metadata.components.enums import IdType
from anime_list_apis.api.AnilistApi import AnilistApi
from anime_list_apis.models.attributes.Id import IdType as AnimeListIdType
from anime_list_apis.models.attributes.MediaType import MediaType
from anime_list_apis.models.attributes.ConsumingStatus import ConsumingStatus
from anime_list_apis.models.attributes.ReleasingStatus import ReleasingStatus


class TvSeriesChecker(Checker):
    """
    Class that check TV Series media for consistency
    """

    def check(self) -> bool:
        """
        Performs sanity checks and prints out anything that's wrong
        :return: The result of the check
        """
        valid = super().check()
        valid = self._check_season_metadata() and valid
        valid = self._check_tvdb_ids() and valid

        # Subsequent steps need to have fully valid metadata and tvdb ids
        if not valid:
            return valid

        valid = self._check_tvdb_season_lengths() and valid
        valid = self._check_tvdb_episode_files_complete() and valid
        valid = self._check_spinoff_completeness() and valid

        if self.config.get("anilist_user") is not None:
            valid = self._check_anilist_ids() and valid

        return valid

    def _check_season_metadata(self) -> bool:
        """
        Makes sure that every season directory has a corresponding
        metadata entry.
        :return: The result of the check
        """
        valid = True
        metadata = self.metadata  # type: TvSeries  # type: ignore

        for season_name in os.listdir(metadata.directory_path):
            season_path = os.path.join(metadata.directory_path, season_name)

            if os.path.isfile(season_path) or season_name.startswith("."):
                continue

            try:
                metadata.get_season(season_name)
            except KeyError:
                valid = self.error(
                    "Missing metadata for Season '{}'".format(season_name)
                )

        return valid

    def _check_tvdb_ids(self) -> bool:
        """
        Makes sure that all TVDB Ids are valid and point to actual entries
        on the website.
        :return: The result of the check
        """
        valid = True
        metadata = self.metadata  # type: TvSeries  # type: ignore

        ids = [metadata.tvdb_id]
        for season in metadata.seasons:
            ids.append(season.tvdb_id)

        for tvdb_id in ids:
            if int(tvdb_id) == 0:  # TVDB ID 0 means show not on tvdb
                continue
            try:
                _ = self.tvdb[int(tvdb_id)]
            except tvdb_shownotfound:
                valid = self.error("Entry {} not found on TVDB")

        return valid

    def _check_tvdb_season_lengths(self) -> bool:
        """
        Checks that the length of the seasons are in accordance with the
        amount of episodes on TVDB.
        :return: The result of the check
        """
        valid = True
        metadata = self.metadata  # type: TvSeries  # type: ignore

        ignores = self._generate_ignores_map()
        tvdb_data = self.tvdb[int(metadata.tvdb_id)]

        for season_number, season_data in tvdb_data.items():
            episode_amount = len(season_data)
            for episode_number, episode_data in season_data.items():

                # Don't count unaired episodes
                if not self._has_aired(episode_data):
                    episode_amount -= 1

                # Subtract ignored episodes
                elif episode_number in ignores.get(season_number, []):
                    episode_amount -= 1

            _existing = metadata.get_episode_files()
            existing = _existing[metadata.tvdb_id].get(season_number, [])

            if not len(existing) == episode_amount:
                msg = "Mismatch in season {}; Should:{}; Is:{}".format(
                    season_number, episode_amount, len(existing)
                )
                valid = self.error(msg)

        return valid

    def _check_tvdb_episode_files_complete(self) -> bool:
        """
        Makes sure that all episodes entered on thetvdb.com are present
        in the directory or otherwise excluded using metadata
        :return: The result of the check
        """
        valid = True
        metadata = self.metadata  # type: TvSeries  # type: ignore

        ignores = self._generate_ignores_map()
        tvdb_data = self.tvdb[int(metadata.tvdb_id)]

        for season_number, season_data in tvdb_data.items():
            for episode_number, episode_data in season_data.items():

                if not self._has_aired(episode_data):
                    continue

                # Ignore ignored episode number
                if episode_number in ignores.get(season_number, []):
                    continue

                episode_name = self._generate_episode_name(
                    metadata.tvdb_id, season_number, episode_number
                )

                # Check if file exists
                existing_files = \
                    metadata.get_episode_files()[metadata.tvdb_id].get(
                        season_number, []
                    )

                exists = False
                for episode_file in existing_files:
                    existing_name = os.path.basename(episode_file)
                    if existing_name.startswith(episode_name):
                        exists = True
                        break

                if not exists:
                    valid = self.error(
                        "Episode {} does not exist "
                        "or is incorrectly named".format(episode_name)
                    )

        return valid

    def _check_spinoff_completeness(self) -> bool:
        """
        Makes sure that any spinoff series are also available and complete
        :return: The result of the check
        """
        valid = True
        metadata = self.metadata  # type: TvSeries  # type: ignore
        episode_files = metadata.get_episode_files()

        for season in metadata.seasons:
            if not season.is_spinoff():
                continue

            tvdb_data = self.tvdb[int(season.tvdb_id)][1]

            # Check Length
            should = len(episode_files[season.tvdb_id][1])
            if not len(tvdb_data) == len(episode_files[season.tvdb_id][1]):
                msg = "Mismatch in spinoff {}; Should:{}; Is:{}".format(
                    season.name, should, len(tvdb_data)
                )
                valid = self.error(msg)

            # Check Names
            for episode_number, episode_data in tvdb_data.items():

                if not self._has_aired(episode_data):
                    continue

                name = self._generate_episode_name(
                    season.tvdb_id, 1, episode_number, season.name
                )

                exists = False
                for episode_file in os.listdir(season.path):
                    if episode_file.startswith(name):
                        exists = True

                if not exists:
                    valid = self.error(
                        "Episode {} does not exist "
                        "or is incorrectly named".format(name)
                    )
        return valid

    def _check_anilist_ids(self) -> bool:
        """
        Makes sure that every season has at least one anilist ID and that
        each anilist ID is entered as "Completed" as long as the series
        has already aired
        :return: The check result
        """

        metadata = self.metadata  # type: TvSeries  # type: ignore
        api = self.config["anilist_api"]  # type: AnilistApi
        user_list = self.config["anilist_anime_list"]
        completed_ids = list(
            map(
                lambda x: int(x.id.get(AnimeListIdType.ANILIST)),
                filter(
                    lambda x: x.consuming_status == ConsumingStatus.COMPLETED,
                    user_list
                )
            )
        )
        valid = True

        for season in metadata.seasons:

            mal_ids = None
            if IdType.MYANIMELIST not in season.ids:
                valid = \
                    self.error("No myanimelist ID for {}".format(season.name))
            else:
                mal_ids = season.ids[IdType.MYANIMELIST]

            if IdType.ANILIST not in season.ids:

                valid = self.error("No anilist ID for {}".format(season.name))

                # Fetch IDs based on myanimelist IDs
                print(mal_ids)
                print(self.fix_interactively)
                if mal_ids is not None and self.fix_interactively:
                    anilist_ids = []
                    for mal_id in mal_ids:
                        anilist_id = api.get_anilist_id_from_mal_id(
                            MediaType.ANIME, int(mal_id)
                        )

                        if anilist_id is not None:
                            anilist_ids.append(str(anilist_id))

                    resp = input(
                        "{}Set anilist IDs to {}? (y|n){}".format(
                            Fore.LIGHTGREEN_EX, anilist_ids, Style.RESET_ALL
                        )
                    ).lower().strip()

                    if resp == "y":
                        season_ids = season.ids
                        season_ids[IdType.ANILIST] = anilist_ids
                        season.ids = season_ids
                        self.metadata.write()

            ids = season.ids.get(IdType.ANILIST, [])
            for _id in ids:
                if int(_id) not in completed_ids:
                    data = api.get_anime_data(int(_id))
                    if data.releasing_status == ReleasingStatus.FINISHED:
                        valid = self.error(
                            "ID {} not completed on anilist.com".format(_id)
                        )

        return valid

        # TODO
        # For each ID:
        #   check if amount of episode files is correct
        #   Note: Make sure to think of multi-episodes etc

    def _generate_ignores_map(self) -> Dict[int, List[int]]:
        """
        Generates a dictionary mapping the excluded episode number to their
        respective episodes.
        :return: The generated dictionary: {season: [episodes]}
        """
        metadata = self.metadata  # type: TvSeries  # type: ignore
        ignores = {}  # type: Dict[int, List[int]]

        excluded = metadata.excludes.get(IdType.TVDB, {})
        multis = metadata.multi_episodes.get(IdType.TVDB, {})
        start_overrides = \
            metadata.season_start_overrides.get(IdType.TVDB, {})

        # Add excluded episodes directly
        for season, episodes in excluded.items():
            ignores[season] = ignores.get(season, []) + episodes

        # Add all episodes in a multi episode besides the first one
        for season, _multis in multis.items():
            for start, end in _multis.items():
                ignore = list(range(start + 1, end + 1))
                ignores[season] = ignores.get(season, []) + ignore

        # Ignore all episodes before the overridden start
        for season, start in start_overrides.items():
            ignore = list(range(1, start))
            ignores[season] = ignores.get(season, []) + ignore

        return ignores

    def _generate_episode_name(
            self,
            tvdb_id: str,
            season_number: int,
            episode_number: int,
            series_name_override: Optional[str] = None
    ):
        """
        Generates an episode name
        :param tvdb_id: The TVDB ID for which to generate the name
        :param season_number: The season number for which to generate the name
        :param episode_number: The episode number for which to gen the name
        :param series_name_override: Overrides the series name
        :return: The generated name
        """
        metadata = self.metadata  # type: TvSeries  # type: ignore
        multis = metadata.multi_episodes.get(IdType.TVDB, {})

        series_name = metadata.name
        if series_name_override is not None:
            series_name = series_name_override

        end = None
        if episode_number in multis.get(season_number, {}):
            end = multis[season_number][episode_number]

        return RenameOperation.sanitize(
            metadata.directory_path,
            Renamer.generate_tv_episode_filename(
                "",
                series_name,
                season_number,
                episode_number,
                Renamer.load_tvdb_episode_name(
                    tvdb_id,
                    season_number,
                    episode_number,
                    end
                ),
                end
            )
        )

    @staticmethod
    def _has_aired(episode_data: dict) -> bool:
        """
        Checks whether or not an episode has already aired or not
        :param episode_data: The episode data to check
        :return: True if already aired, False otherwise
        """
        airdate = episode_data["firstAired"]
        now = datetime.now().strftime("%Y-%m-%d")
        return airdate < now and airdate
