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


# DO NOT BEAUTIFY THIS FILE
from .patterns import *
from .messages import ChannelMessage, PartMessage, Message, JoinMessage, NoticeMessage, PingMessage, auto_message, \
    process_twitch_flags, PongMessage, WhisperMessage, ReconnectMessage
from .connection import Connection
from .command import Command
from .bot import Bot

from .bot_storage import JsonStorage, CannotLoadError, AmbiguousSaveError
from .logging import info, warn, log, log_file, log_rotate_delay, rotate_logs, enable_file_logging, LOG_FORMAT, \
    DISPLAY_LOG_LEVELS
from .permissions import require_permission, auto_group, PermissionList
from .permission_names import *
from .stock_commands import get_no_permission_generator, get_quit_command, get_part_command, get_join_command, \
    get_perm_command
from .argument_parser import ArgumentParser