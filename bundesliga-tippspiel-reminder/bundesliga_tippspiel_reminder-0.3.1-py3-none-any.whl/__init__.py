"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of otaku-info-bot.

otaku-info-bot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

otaku-info-bot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with otaku-info-bot.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

import pkg_resources


sentry_dsn = "https://bb7b3f62b88d48309ed1539af4a53b6a@sentry.namibsun.net/5"
"""
The sentry DSN for this project
"""


version = pkg_resources.get_distribution("bundesliga_tippspiel_reminder")\
    .version
"""
The current version of otaku_info_bot
"""
