#!/usr/bin/python3
import os
import subprocess
import json
from iot_message.exception import DecryptNotFound
from iot_message.exception import NoDecodersDefined

__author__ = 'Bartosz Kościów'


class Message(object):
    """Class Message"""
    protocol = "iot:1"
    chip_id = None
    node_name = None
    encoders = []
    decoders = {}
    drop_unencrypted = False

    def __init__(self):
        if self.chip_id is None:
            self.chip_id = self._get_id()

        if self.node_name is None:
            self.node_name = self._get_node_name()

        self.data = None
        self.encoder = 0

    @classmethod
    def add_decoder(cls, decoder):
        cls.decoders[decoder.name] = decoder

    @classmethod
    def add_encoder(cls, encoder):
        cls.encoders.append(encoder)

    def _get_id(self):
        """:return string"""
        if 'nt' in os.name:
            return subprocess.getoutput('wmic csproduct get uuid')
        else:
            return subprocess.getoutput('cat /var/lib/dbus/machine-id')

    def _get_node_name(self):
        import socket
        return socket.gethostname()

    def _initialize_data(self):
        self.data = {
            'protocol': self.protocol,
            'node': self.node_name,
            'chip_id': self.chip_id,
            'event': '',
            'parameters': {},
            'response': '',
            'targets': [
                'ALL'
            ]
        }

    def clear(self):
        self._initialize_data()

    def set(self, data):
        if self.data is None:
            self._initialize_data()

        for k, v in data.items():
            self.data[k] = v

    def encrypt(self):
        if len(self.encoders) > 0:
            self.encoders[self.encoder].encrypt(self)

    def decrypt(self):
        if len(self.data['event']) > 8 and self.data['event'][0:8] == "message.":
            if self.data['event'] in self.decoders:
                self.decoders[self.data['event']].decrypt(self)
            else:
                raise DecryptNotFound("Decryptor %s not found".format(self.data['event']))
        else:
            if self.drop_unencrypted:
                if len(self.decoders) > 0:
                    self.data = None
                else:
                    raise NoDecodersDefined("Encryption required but decoders empty")

    def __bytes__(self):
        self.encrypt()
        return json.dumps(self.data).encode()

    def __repr__(self):
        return json.dumps(self.data)

    def __getitem__(self, item):
        return self.data[item]