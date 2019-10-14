"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of bundesliga-tippspiel-reminder (btr).

btr is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

btr is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with btr.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from typing import List
from kudubot.parsing.Command import Command
from kudubot.parsing.CommandParser import CommandParser


class BundesligaTippspielReminderParser(CommandParser):
    """
    Parser for the bot that defines the available commands
    """

    @classmethod
    def name(cls) -> str:
        """
        :return: The name of the bot
        """
        return "bundesliga-tippspiel-reminder"

    @classmethod
    def commands(cls) -> List[Command]:
        """
        :return: The available commands
        """
        return [
            Command("login", [("username", str), ("password", str)]),
            Command("is_authorized", []),
            Command("leaderboard", []),
            Command("reminder_state", []),
            Command("activate_reminder", [("hours", int)]),
            Command("deactivate_reminder", [])
        ]
