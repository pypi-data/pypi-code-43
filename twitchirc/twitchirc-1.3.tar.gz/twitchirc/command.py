#  Library to make crating bots for Twitch chat easier.
#  Copyright (c) 2019 Maciej Marciniak
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import typing

import twitchirc

Bot = typing.TypeVar('Bot')


class Command:
    def __init__(self, chat_command: str, function: typing.Callable, parent: Bot,
                 forced_prefix: typing.Optional[str] = None, enable_local_bypass: bool = True,
                 matcher_function: typing.Optional[typing.Callable[[twitchirc.ChannelMessage,
                                                                    typing.Any], bool]] = None,
                 limit_to_channels: typing.Optional[typing.List[str]] = None):
        self.matcher_function = matcher_function
        self.enable_local_bypass = enable_local_bypass
        self.ef_command = (forced_prefix + chat_command + ' ') if forced_prefix is not None else chat_command + ' '
        self.chat_command = chat_command
        self.function = function
        self.permissions_required = []
        self.forced_prefix = forced_prefix
        self.parent = parent
        self.limit_to_channels = limit_to_channels

    def __call__(self, message: twitchirc.ChannelMessage):
        if self.permissions_required:
            o = self.parent.check_permissions_from_command(message, self)
            if o:  # a non-empty list of missing permissions.
                return
        if self.limit_to_channels is not None and message.channel not in self.limit_to_channels:
            return
        self.function(message)
