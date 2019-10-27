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

from .message import Message

import dkd  # dkd.InstantMessage, dkd.ReliableMessage


class SecureMessage(Message):
    """Instant Message encrypted by a symmetric key

        Secure Message
        ~~~~~~~~~~~~~~

        data format: {
            //-- envelope
            sender   : "moki@xxx",
            receiver : "hulk@yyy",
            time     : 123,
            //-- content data & key/keys
            data     : "...",  // base64_encode(symmetric)
            key      : "...",  // base64_encode(asymmetric)
            keys     : {
                "ID1": "key1", // base64_encode(asymmetric)
            }
        }
    """

    def __new__(cls, msg: dict):
        """
        Create secure message

        :param msg: message info
        :return: SecureMessage object
        """
        if msg is None:
            return None
        elif cls is SecureMessage:
            if 'signature' in msg:
                # this should be a reliable message
                # noinspection PyTypeChecker
                return dkd.ReliableMessage.__new__(dkd.ReliableMessage, msg)
            elif isinstance(msg, SecureMessage):
                # return SecureMessage object directly
                return msg
        # subclass or SecureMessage(dict)
        return super().__new__(cls, msg)

    def __init__(self, msg: dict):
        if self is msg:
            # no need to init again
            return
        super().__init__(msg)
        # lazy
        self.__data: bytes = None
        self.__key: bytes = None
        self.__keys: dict = None
        self.__delegate = None  # ISecureMessageDelegate

    @property
    def data(self) -> bytes:
        if self.__data is None:
            base64 = self.get('data')
            assert base64 is not None, 'secure message data cannot be empty'
            self.__data = self.delegate.decode_data(data=base64, msg=self)
        return self.__data

    @property
    def encrypted_key(self) -> bytes:
        if self.__key is None:
            base64 = self.get('key')
            if base64 is None:
                # check 'keys'
                keys = self.encrypted_keys
                if keys is not None:
                    base64 = keys.get(self.envelope.receiver)
            if base64 is not None:
                self.__key = self.delegate.decode_key(key=base64, msg=self)
        return self.__key

    @property
    def encrypted_keys(self) -> dict:
        if self.__keys is None:
            self.__keys = self.get('keys')
        return self.__keys

    @property
    def delegate(self):  # ISecureMessageDelegate
        return self.__delegate

    @delegate.setter
    def delegate(self, delegate):
        self.__delegate = delegate

    """
        Decrypt the Secure Message to Instant Message
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            +----------+      +----------+
            | sender   |      | sender   |
            | receiver |      | receiver |
            | time     |  ->  | time     |
            |          |      |          |  1. PW      = decrypt(key, receiver.SK)
            | data     |      | content  |  2. content = decrypt(data, PW)
            | key/keys |      +----------+
            +----------+
    """

    def decrypt(self):  # -> InstantMessage
        """
        Decrypt message data to plaintext content

        :return: InstantMessage object
        """
        sender = self.envelope.sender
        receiver = self.envelope.receiver
        group = self.envelope.group

        # 1. decrypt 'message.key' to symmetric key
        # 1.1. decode encrypted key data
        key = self.encrypted_key
        # 1.2. decrypt key data
        #      if key is empty, means it should be reused, get it from key cache
        if group is None:
            # personal message
            password = self.delegate.decrypt_key(key=key, sender=sender, receiver=receiver, msg=self)
        else:
            # group message
            password = self.delegate.decrypt_key(key=key, sender=sender, receiver=group, msg=self)

        # 2. decrypt 'message.data' to 'message.content'
        # 2.1. decode encrypted content data
        data = self.data
        # 2.2. decrypt & deserialize content data
        content = self.delegate.decrypt_content(data=data, key=password, msg=self)
        # 2.3. check attachment for File/Image/Audio/Video message content
        #      if file data not download yet,
        #          decrypt file data with password;
        #      else,
        #          save password to 'message.content.password'.
        #      (do it in 'core' module)
        if content is None:
            raise ValueError('failed to decrypt message content from secure message: %s' % self)

        # 3. pack message
        msg = self.copy()
        msg.pop('key', None)
        msg.pop('keys', None)
        msg.pop('data')
        msg['content'] = content
        return dkd.InstantMessage(msg)

    """
        Sign the Secure Message to Reliable Message
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            +----------+      +----------+
            | sender   |      | sender   |
            | receiver |      | receiver |
            | time     |  ->  | time     |
            |          |      |          |
            | data     |      | data     |
            | key/keys |      | key/keys |
            +----------+      | signature|  1. signature = sign(data, sender.SK)
                              +----------+
    """

    def sign(self):  # -> ReliableMessage
        """
        Sign the message.data with sender's private key

        :return: ReliableMessage object
        """
        # 1. sign message.data
        env = self.envelope
        signature = self.delegate.sign_data(data=self.data, sender=env.sender, msg=self)
        assert signature is not None, 'failed to sign message: %s' % self

        # 2. pack message
        msg = self.copy()
        msg['signature'] = self.delegate.encode_signature(signature=signature, msg=self)
        return dkd.ReliableMessage(msg)

    """
        Split/Trim group message
        ~~~~~~~~~~~~~~~~~~~~~~~~
        
        for each members, get key from 'keys' and replace 'receiver' to member ID
    """

    def split(self, members: list) -> list:
        """
        Split the group message to single person messages

        :param members: All group members
        :return:        A list of SecureMessage objects for all group members
        """
        msg = self.copy()
        # check 'keys'
        keys = msg.get('keys')
        if keys is None:
            keys = {}
        else:
            msg.pop('keys')
        # check 'signature'
        reliable = 'signature' in msg

        # 1. move the receiver(group ID) to 'group'
        #    this will help the receiver knows the group ID
        #    when the group message separated to multi-messages;
        #    if don't want the others know your membership,
        #    DON'T do this.
        msg['group'] = self.envelope.receiver

        messages = []
        for member in members:
            # 2. change 'receiver' to each group member
            msg['receiver'] = member
            # 3. get encrypted key
            key = keys.get(member)
            if key is None:
                msg.pop('key', None)
            else:
                msg['key'] = key
            # 4. pack message
            if reliable:
                messages.append(dkd.ReliableMessage(msg))
            else:
                messages.append(SecureMessage(msg))
        # OK
        return messages

    def trim(self, member: str):  # -> SecureMessage
        """
        Trim the group message for a member

        :param member: Member ID
        :return:       A SecureMessage object drop all irrelevant keys to the member
        """
        msg = self.copy()
        # trim keys
        keys = msg.get('keys')
        if keys is not None:
            # move key data from 'keys' to 'key'
            key = keys.get(member)
            if key is not None:
                msg['key'] = key
            msg.pop('keys')
        # check 'group'
        group = self.envelope.group
        if group is None:
            # if 'group' not exists, the 'receiver' must be a group ID here, and
            # it will not be equal to the member of course,
            # so move 'receiver' to 'group'
            msg['group'] = self.envelope.receiver
        # replace receiver
        msg['receiver'] = member
        # repack
        if 'signature' in msg:
            return dkd.ReliableMessage(msg)
        else:
            return SecureMessage(msg)
