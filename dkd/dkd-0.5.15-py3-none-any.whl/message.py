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

import dkd  # dkd.InstantMessage, dkd.ReliableMessage


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

    def __new__(cls, msg: dict):
        """
        Create message

        :param msg: message info
        :return: Message object
        """
        if msg is None:
            return None
        elif cls is Message:
            if 'content' in msg:
                # this should be an instant message
                return super().__new__(dkd.InstantMessage, msg)
            elif 'signature' in msg:
                # this should be a reliable message
                return super().__new__(dkd.ReliableMessage, msg)
            elif 'data' in msg:
                # this should be a secure message
                return super().__new__(dkd.SecureMessage, msg)
            elif isinstance(msg, Message):
                # return Message object directly
                return msg
        # subclass
        # noinspection PyTypeChecker
        return super().__new__(cls, msg)

    def __init__(self, msg: dict):
        if self is msg:
            # no need to init again
            return
        super().__init__(msg)
        # message envelope
        self.__envelope: Envelope = None

    @property
    def envelope(self) -> Envelope:
        if self.__envelope is None:
            # let envelope share the same dictionary with message
            self.__envelope = Envelope(self)
        return self.__envelope
