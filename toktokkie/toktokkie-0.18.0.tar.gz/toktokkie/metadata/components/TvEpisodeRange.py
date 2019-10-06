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

from typing import Dict, Any, List
from toktokkie.metadata.components.TvEpisode import TvEpisode
from toktokkie.exceptions import InvalidMetadata


class TvEpisodeRange:
    """
    Class that models a TV Episode Range
    """

    def __init__(self, json_data: Dict[str, Any]):
        """
        Initializes the TvEpisodeRange object
        :param json_data: The JSON data from which to generate
                          the episode range from
        :raises InvalidMetadataException: If the provided JSON is invalid
        """
        self.json = json_data

        try:
            self.season = json_data["season"]
            self.start_episode = json_data["start_episode"]
            self.end_episode = json_data["end_episode"]
        except (KeyError, TypeError):
            raise InvalidMetadata()

    @property
    def episodes(self) -> List[TvEpisode]:
        """
        :return: A list of episodes included in this episode range
        """
        episodes = []
        min_episode = min(self.start_episode, self.end_episode)
        max_episode = min(self.start_episode, self.end_episode)

        for episode in range(min_episode, max_episode + 1):
            episodes.append(TvEpisode({
                "season": self.season,
                "episode": episode
            }))

        return episodes
