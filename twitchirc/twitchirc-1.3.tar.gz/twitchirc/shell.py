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
import typing

import twitchirc


def create_msg(text, channel) -> twitchirc.ChannelMessage:
    """
    Create a ChannelMessage with the provided text and channel.

    :return: Newly created ChannelMessage object.
    """
    msg = twitchirc.ChannelMessage(text=text, channel=channel, user='OUTGOING')
    msg.outgoing = True
    return msg


def connect(oauth_token, use_ssl=True) -> twitchirc.Connection:
    """
    Connect to IRC.

    :param oauth_token: Authentication token. The username is not needed for connecting. You can get one at
    https://twitchapps.com/tmi/
    :param use_ssl: You can enable or disable encryption here.
    :return: created connection.
    """
    conn = twitchirc.Connection('irc.chat.twitch.tv', port=6697 if use_ssl else 6667, secure=use_ssl)
    conn.connect('don_t_need_to_know_this', oauth_token)
    return conn


received_messages = []


def recv(conn: twitchirc.Connection) -> typing.List[twitchirc.Message]:
    global received_messages
    msgs = []
    while 1:
        conn.receive()
        m = conn.process_messages()
        if not m:
            break
        msgs.extend(m)

    received_messages = msgs.copy()
    for i in msgs:
        print(i)


print(f'twitchirc shell shortcuts loaded. There are shortcuts here for making experimenting easier.')
print(' - create_msg(text, channel) Creates a ChannelMessage with the provided text and channel, useful for sending '
      'test messages.')
print(' - connect(oauth_token, use_ssl=True) Connect')
if __name__ == '__main__':
    try:
        import IPython

        IPython.start_ipython()
    except ImportError:
        import code

        code.interact(local=globals())
