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

# PATTERN SNIPPETS
TWITCH_ARGS_PATTERN = r'(@[^ ]+)'
CHANNEL_PATTERN = r'([a-z0-9A-Z_]+)'
USER_PATTERN = r'([a-zA-Z0-9_-]+)!.+?'

# PATTERNS
PRIVMSG_PATTERN_TWITCH = fr'{TWITCH_ARGS_PATTERN} :{USER_PATTERN} PRIVMSG #{CHANNEL_PATTERN} :(.*)'
PING_MESSAGSE_PATTERN = r'PING :(.*)'
NOTICE_MESSAGE_PATTERN = fr'{TWITCH_ARGS_PATTERN} :(.+) NOTICE #{CHANNEL_PATTERN} :(.*)'
GLOBAL_NOTICE_MESSAGE_PATTERN = fr':(.+) NOTICE \* :(.*)'
JOIN_MESSAGE_PATTERN = rf':{USER_PATTERN} JOIN #{CHANNEL_PATTERN}'
PART_MESSAGE_PATTERN = rf':{USER_PATTERN} PART #{CHANNEL_PATTERN}'
USERNOTICE_MESSAGE_PATTERN = rf'{TWITCH_ARGS_PATTERN} :tmi.twitch.tv USERNOTICE #{CHANNEL_PATTERN}'
WHISPER_MESSAGE_PATTERN = rf'{TWITCH_ARGS_PATTERN} :{USER_PATTERN} WHISPER {CHANNEL_PATTERN} :(.*)'
RECONNECT_MESSAGE_PATTERN = rf':tmi.twitch.tv RECONNECT'

# Delete the pattern snippets
del TWITCH_ARGS_PATTERN, CHANNEL_PATTERN, USER_PATTERN
__all__ = ['PRIVMSG_PATTERN_TWITCH', 'PING_MESSAGSE_PATTERN', 'NOTICE_MESSAGE_PATTERN', 'JOIN_MESSAGE_PATTERN',
           'PART_MESSAGE_PATTERN', 'GLOBAL_NOTICE_MESSAGE_PATTERN', 'WHISPER_MESSAGE_PATTERN',
           'RECONNECT_MESSAGE_PATTERN']
