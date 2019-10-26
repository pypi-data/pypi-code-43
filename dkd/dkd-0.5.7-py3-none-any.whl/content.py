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

import random
from typing import Union


def random_positive_integer():
    """
    :return: random integer greater than 0
    """
    return random.randint(1, 2**32-1)


class Content(dict):
    """This class is for creating message content

        Message Content
        ~~~~~~~~~~~~~~~

        data format: {
            'type'    : 0x00,            // message type
            'sn'      : 0,               // serial number

            'group'   : 'Group ID',      // for group message

            //-- message info
            'text'    : 'text',          // for text message
            'command' : 'Command Name',  // for system command
            //...
        }
    """

    # noinspection PyTypeChecker
    def __new__(cls, content: dict):
        """
        Create message content

        :param content: content info
        :return: Content object
        """
        if content is None:
            return None
        elif cls is Content:
            if isinstance(content, Content):
                # return Content object directly
                return content
            # get subclass by message content type
            clazz = message_content_classes.get(int(content['type']))
            if clazz is not None:
                assert issubclass(clazz, Content), '%s must be sub-class of Content' % clazz
                return clazz(content)
        # subclass or default Content(dict)
        return super().__new__(cls, content)

    def __init__(self, content: dict):
        super().__init__(content)
        # message type: text, image, ...
        self.__type: int = int(content['type'])
        # serial number: random number to identify message content
        self.__sn: int = int(content['sn'])

    # message content type: text, image, ...
    @property
    def type(self) -> int:
        return self.__type

    # random number to identify message content
    @property
    def serial_number(self) -> int:
        return self.__sn

    # Group ID/string for group message
    #    if field 'group' exists, it means this is a group message
    @property
    def group(self) -> str:
        return self.get('group')

    @group.setter
    def group(self, value: str):
        if value is None:
            self.pop('group', None)
        else:
            self['group'] = value

    #
    #   Factory
    #
    @classmethod
    def new(cls, content: Union[int, dict]):
        if isinstance(content, int):
            # create with content type
            dictionary = {
                'type': content,
                'sn': random_positive_integer(),
            }
        elif isinstance(content, dict):
            assert 'type' in content, 'content type error: %s' % content
            dictionary = content
            if 'sn' not in dictionary:
                dictionary['sn'] = random_positive_integer()
        else:
            raise TypeError('message content error: %s' % content)
        # new Content(dict)
        return cls(dictionary)


"""
    Message Content Classes Map
"""

message_content_classes = {
}
