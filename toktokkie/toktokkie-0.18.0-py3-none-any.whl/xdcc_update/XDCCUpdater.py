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
import re
import json
from typing import Dict, Optional, Set, Any, Union
from xdcc_dl.xdcc import download_packs
from xdcc_dl.pack_search.SearchEngine import SearchEngineType, SearchEngine
from toktokkie.renaming import Renamer, RenameOperation
from toktokkie.metadata.TvSeries import TvSeries
from toktokkie.metadata.components.TvSeason import TvSeason
from toktokkie.xdcc_update.enums import Resolution
from toktokkie.exceptions import MissingXDCCInstructions, \
    InvalidXDCCInstructions


class XDCCUpdater:
    """
    Class that handles the configuration and execution of a xdcc-update
    """

    predefined_patterns = {
        "horriblesubs": "[HorribleSubs] @{NAME} - @{EPI-2} [@{RES-P}].mkv"
    }
    """
    A collection of predefined patterns
    """

    def __init__(self, metadata: TvSeries):
        """
        Initializes the XDCC Updater object
        :param metadata: The metadata for the series for which to execute
                         an xdcc-update
        """
        self.metadata = metadata
        self.xdcc_info_file = os.path.join(
            metadata.directory_path,
            ".meta/xdcc-info.json"
        )

        if not os.path.isfile(self.xdcc_info_file):
            raise MissingXDCCInstructions(self.xdcc_info_file)

        with open(self.xdcc_info_file, "r") as xdcc_info:
            self.xdcc_info = json.load(xdcc_info)  # type: Dict[str, Any]

        self._verify_json()

    @property
    def season(self) -> TvSeason:
        """
        :return: The season to update
        """
        season_name = self.xdcc_info["season"]
        for season in self.metadata.seasons:
            if season.name == season_name:
                return season
        raise InvalidXDCCInstructions("Invalid Season {}".format(season_name))

    @property
    def search_name(self) -> str:
        """
        :return: The name of the series for searching purposes
        """
        return self.xdcc_info["search_name"]

    @property
    def search_engine(self) -> SearchEngine:
        """
        :return: The search engine to use
        """
        search_engine = self.xdcc_info["search_engine"]
        resolved = SearchEngineType.resolve(search_engine)
        if resolved is None:
            raise InvalidXDCCInstructions(
                "Invalid Search Engine {}".format(search_engine)
            )
        else:
            return resolved

    @property
    def bot(self) -> str:
        """
        :return: The bot to use for updating
        """
        return self.xdcc_info["bot"]

    @property
    def resolution(self) -> Resolution:
        """
        :return: The resolution in which to update the series
        """
        resolution = self.xdcc_info["resolution"]
        try:
            return Resolution(resolution)
        except ValueError:
            raise InvalidXDCCInstructions(
                "Invalid resolution {}".format(resolution)
            )

    @property
    def p_resolution(self) -> str:
        """
        :return: The resolution in P-notation (1080p)
        """
        return self.resolution.value

    @property
    def x_resolution(self) -> str:
        """
        :return: The resolution in X-notation (1920x1080)
        """
        if self.resolution == Resolution.X1080p:
            return "1920x1080"
        elif self.resolution == Resolution.X720p:
            return "1280x720"
        else:  # self.resolution == Resolution.X480p
            return "720x480"

    @property
    def episode_offset(self) -> int:
        """
        :return: The amount of episodes offset from 1 when updating
        """
        return int(self.xdcc_info["episode_offset"])

    @property
    def search_pattern(self) -> str:
        """
        :return: The search pattern to use
        """
        pattern = self.xdcc_info["search_pattern"]

        if pattern in self.predefined_patterns:
            return self.predefined_patterns[pattern]
        else:
            return pattern

    def _generate_search_term(self, episode: int, regex: bool) -> str:
        """
        Generates a search term/search term regex for a specified episode
        :param episode: The episode for which to generate the search term
        :param regex: Whether or not to generate a regex.
        :return: The generated search term/regex
        """

        pattern = self.search_pattern
        pattern = pattern.replace("@{NAME}", self.search_name)
        pattern = pattern.replace("@{RES-P}", self.p_resolution)
        pattern = pattern.replace("@{RES-X}", self.x_resolution)

        if regex:
            pattern = pattern.replace("[", "\\[")
            pattern = pattern.replace("]", "\\]")
            pattern = pattern.replace("(", "\\(")
            pattern = pattern.replace(")", "\\)")
            pattern = pattern.replace("@{HASH}", "[a-zA-Z0-9]+")
            pattern = pattern.replace(
                "@{EPI-1}", str(episode).zfill(1) + "(v[0-9]+)?"
            )
            pattern = pattern.replace(
                "@{EPI-2}", str(episode).zfill(2) + "(v[0-9]+)?"
            )
            pattern = pattern.replace(
                "@{EPI-3}", str(episode).zfill(3) + "(v[0-9]+)?"
            )

        else:
            pattern = pattern.replace("@{EPI-1}", str(episode).zfill(1))
            pattern = pattern.replace("@{EPI-2}", str(episode).zfill(2))
            pattern = pattern.replace("@{EPI-3}", str(episode).zfill(3))
            pattern = pattern.replace("[@{HASH}]", "")
            pattern = pattern.replace("@{HASH}", "")

        return pattern

    # noinspection PyStatementEffect
    def _verify_json(self):
        """
        Makes sure that all JSON properties are present and valid
        :return: None
        :raises InvalidXDCCInstructions if the JSON data was invalid
        """
        try:
            self.season
            self.search_name
            self.search_engine
            self.bot
            self.resolution
            self.episode_offset
            self.search_pattern
        except KeyError as e:
            raise InvalidXDCCInstructions("Missing key: ".format(str(e)))

    @staticmethod
    def _input(
            prompt_text: str,
            default: Optional[str] = None,
            choices: Optional[Set[str]] = None,
            is_int: bool = False
    ) -> Union[str, int]:
        """
        Creates a user prompt
        :param prompt_text: The text to show the user
        :param default: An optional default parameter
        :param choices: An optional set of valid choices
        :param is_int: If True, will make sure that the response is an integer
        :return: The user-provided response
        """

        prompt_string = prompt_text
        if choices is not None:
            prompt_string = "{} {}".format(prompt_string, choices)
        if default is not None:
            prompt_string = "{} [{}]".format(prompt_string, default)
        prompt_string = "{}:  ".format(prompt_string)

        while True:
            resp = input(prompt_string)

            if resp == "":
                if default is not None:
                    resp = default
                else:
                    continue
            elif choices is not None and resp not in choices:
                continue
            else:
                pass

            if is_int:
                try:
                    return int(resp)
                except ValueError:
                    print("Not an Integer")
            else:
                return resp

    @classmethod
    def prompt(cls, metadata: TvSeries):
        """
        Creates a new XDCC Update instruction set for a given metadata
        :param metadata: The metadata for which to generate the instructions
        :return: The generated XDCCUpdater object
        """

        hs = SearchEngineType.HORRIBLESUBS.name.lower()

        print(
            "Generating XDCC Update instructions for {}".format(metadata.name)
        )

        json_data = {
            "season": cls._input("Season"),
            "search_name": cls._input("Search Name", default=metadata.name),
            "search_engine": cls._input(
                "Search Engine",
                default=hs,
                choices=SearchEngineType.choices()
            ),
            "bot": cls._input("Bot", default="CR-HOLLAND|NEW"),
            "resolution": cls._input(
                "Resolution",
                default="1080p",
                choices={"1080p", "720p", "480p"}
            ),
            "episode_offset": cls._input(
                "Episode Offset", default="0", is_int=True
            )
        }

        print("-" * 80)
        print("Valid variables for search patterns:")

        for variable in [
            "@{NAME}",
            "@{RES-P}",
            "@{RES-X}",
            "@{HASH}",
            "@{EPI-1}",
            "@{EPI-2}",
            "@{EPI-3}"
        ]:
            print(variable)

        print("-" * 80)
        print("Predefined patterns:")

        for pattern in cls.predefined_patterns:
            print(pattern)

        print("-" * 80)
        json_data["search_pattern"] = \
            cls._input("Search Pattern", default="horriblesubs")

        xdcc_info_file = os.path.join(
            metadata.directory_path,
            ".meta/xdcc-info.json"
        )
        with open(xdcc_info_file, "w") as xdcc_info:
            xdcc_info.write(json.dumps(
                json_data,
                sort_keys=True,
                indent=4,
                separators=(",", ": ")
            ))

    def update(self):
        """
        Executes the XDCC Update procedure
        :return: None
        """
        print(self.metadata.name)

        self._update_episode_names()

        start_episode = 1 + len(os.listdir(self.season.path))
        start_episode += self.episode_offset
        packs = []

        episode_count = start_episode

        while True:
            search_term = self._generate_search_term(episode_count, False)
            search_regex = self._generate_search_term(episode_count, True)
            search_results = self.search_engine.search(search_term)

            search_regex = re.compile(search_regex)
            search_results = list(filter(
                lambda x: re.match(search_regex, x.filename)
                and x.bot == self.bot,
                search_results
            ))

            if len(search_results) > 0:
                pack = search_results[0]

                try:
                    ext = "." + pack.filename.rsplit(".")[1]
                except IndexError:
                    ext = ""

                episode_number = episode_count - self.episode_offset
                episode_name = "{} - S{}E{} - Episode {}{}".format(
                    self.metadata.name,
                    str(self.season.season_number).zfill(2),
                    str(episode_number).zfill(2),
                    episode_number,
                    ext
                )
                episode_name = RenameOperation.sanitize(
                    self.season.path, episode_name
                )

                pack.set_directory(self.season.path)
                pack.set_filename(episode_name, True)
                pack.set_original_filename(
                    pack.original_filename.replace("'", "_")
                )  # Fixes filenames

                packs.append(pack)
                episode_count += 1

            else:
                break

        download_packs(packs)
        self._update_episode_names()

    def _update_episode_names(self):
        """
        Renames the episodes in the season directory that's being updated
        :return: None
        """
        renamer = Renamer(self.metadata)
        for operation in renamer.operations:
            operation_dir = os.path.basename(os.path.dirname(operation.source))
            if operation_dir == self.season.name:
                operation.rename()
