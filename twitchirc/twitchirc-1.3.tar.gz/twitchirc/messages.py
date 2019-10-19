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

import re
import typing

import twitchirc


def process_twitch_flags(flags) -> typing.Dict[str, typing.Union[str, typing.List[str]]]:
    # @<key>=<value>;[...]
    flags = flags[1:].split(';')
    # [<key>=<value>, [...]]
    output = {}
    for i in flags:
        i = i.split('=', 1)
        val = i[1]
        if ',' in val:
            val = val.split(',')
        output[i[0]] = val
    return output


class Message:
    @staticmethod
    def from_match(m: typing.Match[str]):
        """
        Create a new object using a match

        :param m: Match
        :return: The new object
        """
        return Message(m.string)

    @staticmethod
    def from_text(text):
        """
        Create a new object from text

        :param text: Text to create it from.
        :return: The new object
        """
        return Message(text)

    def __init__(self, args: str):
        """
        Message object.

        WARNING: If you receive this object at runtime, that means that, the packet you received is not known to this
        library

        :param args: Text received.
        """
        self._type = 'raw'
        self.args: str = args
        self.outgoing = False

    def __eq__(self, other):
        if isinstance(other, Message):
            return other._type == self._type and other.args == self.args
        else:
            return False

    def __repr__(self):
        return f'Message(args={self.args!r})'

    def __str__(self):
        return f'<Raw IRC message: {self.args!r}>'

    def __bytes__(self):
        if self.outgoing:
            return self.args
        else:
            return b''


class WhisperMessage(Message):
    @staticmethod
    def from_match(m: typing.Match[str]):
        flags = process_twitch_flags(m[1])
        new = WhisperMessage(flags=flags, user_from=m[2], user_to=m[3], text=m[4])
        return new

    def __repr__(self):
        return (f'WhisperMessage(flags={self.flags!r}, user_from={self.user_from!r}, user_to={self.user_to!r}, '
                f'text={self.text!r})')

    def __str__(self):
        return f'{self.user_from} -> {self.user_to}: {self.text}'

    def __bytes__(self):
        if self.outgoing:
            return bytes(f'PRIVMSG #jtv :/w {self.user_to} {self.text}\r\n', 'utf-8')
        else:
            return b''

    def __init__(self, flags, user_from, user_to, text, outgoing=False):
        super().__init__(f'{"Outgoing" if outgoing else ""} WHISPER from {user_from} to {user_to}: {text}')
        self.text = text
        self.user_to = user_to
        self.user_from = user_from
        self.flags = flags
        self.outgoing = outgoing

    def reply(self, text: str):
        new = WhisperMessage(flags={}, user_from='OUTGOING', user_to=self.user_from, text=text, outgoing=True)
        return new


class ChannelMessage(Message):
    @staticmethod
    def from_match(m: typing.Match[str]):
        new = ChannelMessage(text=m[4], user=m[2], channel=m[3])
        new.flags = process_twitch_flags(m[1])
        return new

    @staticmethod
    def from_text(text):

        m = re.match(twitchirc.PRIVMSG_PATTERN_TWITCH, text)
        if m:
            return ChannelMessage.from_match(m)
        else:
            # print(text)
            # text -> ':{user}!{user2?}@{user3?}.{host} PRIVMSG #{chan} :{msg}\r\n'
            text = text.replace('\r\n', '')
            # text -> ':{user}!{user2?}@{user3?}.{host} PRIVMSG #{chan} :{msg}'

            t = text.split(' ', 3)
            # t -> [':{user}!{user2?}@{user3?}.{host}', 'PRIVMSG', '#{chan}', ':{msg}']

            if t[1] != 'PRIVMSG':
                raise Exception(f'Invalid ChannelMessage(PRIVMSG), {text!r}')
            # ====USER====
            # t[0] -> ':{user}!{user2?}@{user3?}.{host}'
            # t[0].split('!', 1) -> [':{user}', '{user2?}@{user3?}.{host}']
            # t[0].split('!', 1)[0] -> ':{user}'
            # t[0].split('!', 1)[0][1:] -> '{user}'
            user = t[0].split('!', 1)[0][1:]

            # ===CHANNEL====
            # t[2] -> '#{chan}'
            # t[2][1:] -> '{chan}'
            channel = t[2][1:]

            # ===MESSAGE===
            # t[3] -> ':{msg}'
            # t[3][1:] -> '{msg}'
            text = t[3][1:]

            return ChannelMessage(text=text, user=user, channel=channel)

    def __init__(self, text: str, user: str, channel: str):
        super().__init__(text)
        self._type = 'PRIVMSG'
        self.flags = {}
        self.text: str = text.replace('\r\n', '')
        self.user = user
        self.channel = channel

    def __repr__(self):
        return 'ChannelMessage(text={!r}, user={!r}, channel={!r})'.format(self.text, self.user, self.channel)

    def __str__(self):
        return '#{chan} <{user}> {text}'.format(user=self.user, text=self.text, chan=self.channel)

    def __bytes__(self):
        if self.outgoing:
            return bytes('PRIVMSG #{chan} :{text}\r\n'.format(chan=self.channel, text=self.text), 'utf-8')
        else:
            return b''

    def reply(self, text: str):
        if text.startswith(('.', '/')):
            text = '/ ' + text
        new = ChannelMessage(text=text, user='OUTGOING', channel=self.channel)
        new.outgoing = True
        return new

    def reply_directly(self, text: str):
        new = WhisperMessage(flags={}, user_from='OUTGOING', user_to=self.user, text=text, outgoing=True)
        return new


class PingMessage(Message):
    @staticmethod
    def from_match(m: typing.Match[str]):
        new = PingMessage()
        new.host = m[1]
        return new

    @staticmethod
    def from_text(text):
        new = PingMessage()
        # PING :{host}
        new.host = text.split(' ', 1)[1][1:].replace('\r\n', '')
        return new

    def __init__(self, host: typing.Optional[str] = None):
        self.host = host
        super().__init__(str(self))

    def __repr__(self):
        return 'PingMessage(host={!r})'.format(self.host)

    def __str__(self):
        return 'PING :{}'.format(self.host)

    def reply(self):
        return PongMessage(self.host)


class PongMessage(Message):
    @staticmethod
    def from_match(m: typing.Match[str]):
        return None

    @staticmethod
    def from_text(text):
        return None

    def __init__(self, host):
        super().__init__(host)
        self.host = host

    def __repr__(self):
        return 'PongMessage(host={!r})'.format(self.host)

    def __str__(self):
        return 'PONG :{}'.format(self.host)

    def __bytes__(self):
        return bytes('PONG :{}\r\n'.format(self.host), 'utf-8')

    def reply(self):
        raise RuntimeError('Cannot reply to a PongMessage.')


class NoticeMessage(Message):
    @staticmethod
    def from_match(m: typing.Match[str]):
        new = NoticeMessage('')
        new.message_id = process_twitch_flags(m[1])['msg-id']
        new.host = m[2]
        new.channel = m[3]
        new.text = m[4]
        # @msg-id=%s :tmi.twitch.tv NOTICE #{chan} :{msg}
        return new

    @staticmethod
    def from_text(text):
        m = re.match(twitchirc.NOTICE_MESSAGE_PATTERN, text)
        if m:
            return NoticeMessage.from_match(m)
        else:
            raise Exception('Invalid NoticeMessage(NOTICE): {!r}'.format(text))

    def __init__(self, text, message_id=None, channel=None, host=None):
        super().__init__(text)
        self.text = text
        self.message_id = message_id
        self.channel = channel
        self.host = host


class GlobalNoticeMessage(NoticeMessage):
    @staticmethod
    def from_match(m: typing.Match[str]):
        new = GlobalNoticeMessage('')
        new.host = m[1]
        new.text = m[2]
        return new

    @staticmethod
    def from_text(text):
        m = re.match(twitchirc.GLOBAL_NOTICE_MESSAGE_PATTERN, text)
        if m:
            return GlobalNoticeMessage.from_match(m)
        else:
            raise Exception('Invalid GlobalNoticeMessage(NOTICE[...]*): {!r}'.format(text))

    def __init__(self, text, host=None):
        super().__init__(text, message_id=None, channel='*', host=host)


class JoinMessage(Message):
    @staticmethod
    def from_match(m: typing.Match[str]):
        new = JoinMessage(m[1], m[2])
        return new

    def __init__(self, user: str, channel: str, outgoing=False):
        super().__init__('{} JOIN {}'.format(user, channel))
        self.user = user
        self.channel = channel
        self.outgoing = outgoing

    def __repr__(self) -> str:
        if self.outgoing:
            return f'JoinMessage(user={self.user!r}, channel={self.channel!r}, outgoing=True)>'
        else:
            return f'JoinMessage(user={self.user!r}, channel={self.channel!r})>'

    def __str__(self):
        if self.outgoing:
            return f'JOIN {self.channel}'
        else:
            return f'{self.user} JOIN {self.channel}'

    def __bytes__(self):
        if self.outgoing:
            return bytes(f'JOIN {self.channel}\r\n', 'utf-8')
        else:
            return b''


class PartMessage(Message):
    @staticmethod
    def from_match(m: typing.Match[str]):
        new = PartMessage(m[1], m[2])
        return new

    def __init__(self, user: str, channel: str):
        super().__init__('{} PART {}'.format(user, channel))
        self.user = user
        self.channel = channel

    def __repr__(self):
        if self.outgoing:
            return f'PartMessage(user={self.user!r}, channel={self.channel!r})  # outgoing'
        else:
            return f'PartMessage(user={self.user!r}, channel={self.channel!r})'

    def __str__(self):
        if self.outgoing:
            return f'<PART {self.channel}>'
        else:
            return f'<{self.user} PART {self.channel}>'


class UsernoticeMessage(Message):
    @staticmethod
    def from_match(m: typing.Match[str]):
        new = UsernoticeMessage(m[1], m[2])
        return new

    def __repr__(self):
        return f'UsernoticeMessage(flags={self.flags!r}, channel={self.channel!r})'

    def __str__(self):
        return f'<USERNOTICE {self.channel}>'

    def __init__(self, flags, channel):
        super().__init__(flags + ' ' + channel)
        self.flags = flags
        self.channel = channel


class ReconnectMessage(Message):
    @staticmethod
    def from_match(m: typing.Match[str]):
        new = ReconnectMessage()
        return new

    def __repr__(self):
        return f'ReconnectMessage()'

    def __str__(self):
        return f'<RECONNECT>'

    def __init__(self):
        super().__init__('RECONNECT')


MESSAGE_PATTERN_DICT: typing.Dict[str, typing.Union[
    typing.Type[ChannelMessage],
    typing.Type[PingMessage],
    typing.Type[NoticeMessage],
    typing.Type[GlobalNoticeMessage],
    typing.Type[JoinMessage],
    typing.Type[PartMessage],
    typing.Type[WhisperMessage],
    typing.Type[ReconnectMessage]
]
] = {
    twitchirc.PRIVMSG_PATTERN_TWITCH: ChannelMessage,
    twitchirc.PING_MESSAGSE_PATTERN: PingMessage,
    twitchirc.NOTICE_MESSAGE_PATTERN: NoticeMessage,
    twitchirc.GLOBAL_NOTICE_MESSAGE_PATTERN: GlobalNoticeMessage,
    twitchirc.JOIN_MESSAGE_PATTERN: JoinMessage,
    twitchirc.PART_MESSAGE_PATTERN: PartMessage,
    twitchirc.WHISPER_MESSAGE_PATTERN: WhisperMessage,
    twitchirc.RECONNECT_MESSAGE_PATTERN: ReconnectMessage
}


def auto_message(message):
    for k, v in MESSAGE_PATTERN_DICT.items():
        m = re.match(k, message)
        if m:
            return v.from_match(m)

    # if nothing matches return generic irc message.
    return Message(message)
