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

import time as time_lib


class Dictionary:
    """
        A container sharing the same inner dictionary
    """

    def __init__(self, dictionary: dict):
        super().__init__()
        self.__dictionary = dictionary

    @property
    def dictionary(self) -> dict:
        return self.__dictionary

    def __setitem__(self, key, value):
        # self.__dictionary.__setitem__(key, value)
        self.__dictionary[key] = value

    def __getitem__(self, key):
        # return self.__dictionary.__getitem__(key)
        return self.__dictionary[key]

    def get(self, key):
        return self.__dictionary.get(key)

    def pop(self, key, default=None):
        return self.__dictionary.pop(key, default)


class Envelope(Dictionary):
    """This class is used to create a message envelope
    which contains 'sender', 'receiver' and 'time'

        Envelope for message
        ~~~~~~~~~~~~~~~~~~~~

        data format: {
            sender   : "moki@xxx",
            receiver : "hulk@yyy",
            time     : 123
        }
    """

    def __new__(cls, env: dict):
        """
        Create message envelope

        :param env: envelope info
        :return: Envelope object
        """
        if env is None:
            return None
        elif cls is Envelope:
            if isinstance(env, Envelope):
                # return Envelope object directly
                return env
        # new Envelope(dict)
        return super().__new__(cls)

    def __init__(self, envelope: dict):
        if self is envelope:
            # no need to init again
            return
        super().__init__(envelope)
        # sender ID string
        self.__sender: str = None
        # receiver ID string
        self.__receiver: str = None
        # timestamp
        self.__time: int = None

    @property
    def sender(self) -> str:
        if self.__sender is None:
            self.__sender = self['sender']
        return self.__sender

    @property
    def receiver(self) -> str:
        if self.__receiver is None:
            self.__receiver = self['receiver']
        return self.__receiver

    @property
    def time(self) -> int:
        if self.__time is None:
            time = self.get('time')
            if time is None:
                self.__time = 0
            else:
                self.__time = int(time)
        return self.__time

    """
        Group ID
        ~~~~~~~~
        when a group message was split/trimmed to a single message
        the 'receiver' will be changed to a member ID, and
        the group ID will be saved as 'group'.
    """
    @property
    def group(self) -> str:
        return self.get('group')

    @group.setter
    def group(self, value: str):
        if value is None:
            self.pop('group', None)
        else:
            self['group'] = value

    """
        Message Type
        ~~~~~~~~~~~~
        because the message content will be encrypted, so
        the intermediate nodes(station) cannot recognize what kind of it.
        we pick out the content type and set it in envelope
        to let the station do its job.
    """
    @property
    def type(self) -> int:
        number = self.get('type')
        if number is None:
            return 0
        else:
            return int(number)

    @type.setter
    def type(self, value: int):
        self['type'] = value

    @classmethod
    def new(cls, sender: str, receiver: str, time: int=0):
        if time == 0:
            time = int(time_lib.time())
        env = {
            'sender': sender,
            'receiver': receiver,
            'time': time
        }
        return cls(env)
