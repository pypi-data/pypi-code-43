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

import tvdb_api
import argparse
from toktokkie.scripts.Command import Command
from anime_list_apis.api.AnilistApi import AnilistApi


class CheckCommand(Command):
    """
    Class that encapsulates behaviour of the check command
    """

    @classmethod
    def name(cls) -> str:
        """
        :return: The command name
        """
        return "check"

    @classmethod
    def prepare_parser(cls, parser: argparse.ArgumentParser):
        """
        Prepares an argumentparser for this command
        :param parser: The parser to prepare
        :return: None
        """
        cls.add_directories_arg(parser)
        parser.add_argument("--warnings", action="store_true",
                            help="Shows warnings in addition to errors")
        parser.add_argument("--fix", action="store_true",
                            help="Enables interactive error fixing")
        parser.add_argument("--anilist-user",
                            help="The username used for anilist checks")

    def execute(self):
        """
        Executes the commands
        :return: None
        """
        config = {
            "tvdb_api": tvdb_api.Tvdb(),
            "anilist_user": self.args.anilist_user
        }

        if self.args.anilist_user is not None:
            api = AnilistApi()
            config["anilist_api"] = api

            anime_list = api.get_anime_list(self.args.anilist_user)
            manga_list = api.get_manga_list(self.args.anilist_user)
            config["anilist_anime_list"] = anime_list
            config["anilist_manga_list"] = manga_list

        for directory in self.load_directories(self.args.directories):
            directory.check(self.args.warnings, self.args.fix, config)
