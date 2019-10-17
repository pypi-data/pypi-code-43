# -*- coding: utf-8 -*-
#
#   Dao-Ke-Dao: Universal Message Module
#
#                                Written in 2019 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2019 Albert Moky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

"""
    Message Transforming
    ~~~~~~~~~~~~~~~~~~~~

        Instant Message <-> Secure Message <-> Reliable Message
        +-------------+     +------------+     +--------------+
        |  sender     |     |  sender    |     |  sender      |
        |  receiver   |     |  receiver  |     |  receiver    |
        |  time       |     |  time      |     |  time        |
        |             |     |            |     |              |
        |  content    |     |  data      |     |  data        |
        +-------------+     |  key/keys  |     |  key/keys    |
                            +------------+     |  signature   |
                                               +--------------+
        Algorithm:
            data      = password.encrypt(content)
            key       = receiver.public_key.encrypt(password)
            signature = sender.private_key.sign(data)
"""

from .envelope import Envelope


class Message(dict):
    """This class is used to create a message
    with the envelope fields, such as 'sender', 'receiver', and 'time'

        Message with Envelope
        ~~~~~~~~~~~~~~~~~~~~~
        Base classes for messages

        data format: {
            //-- envelope
            sender   : "moki@xxx",
            receiver : "hulk@yyy",
            time     : 123,
            //-- body
            ...
        }
    """

    def __init__(self, msg: dict):
        super().__init__(msg)
        # build envelope
        sender = msg['sender']
        receiver = msg['receiver']
        time = msg.get('time')
        if time is None:
            time = 0
        else:
            time = int(time)
        self.__envelope: Envelope = Envelope.new(sender=sender, receiver=receiver, time=time)

    @property
    def envelope(self) -> Envelope:
        return self.__envelope

    """
        Group ID
        ~~~~~~~~
        when a group message was split/trimmed to a single message
        the 'receiver' will be changed to a member ID, and
        the group ID will be saved as 'group'.
    """
    @property
    def group(self) -> str:
        yield None

    @group.setter
    def group(self, identifier: str):
        pass
