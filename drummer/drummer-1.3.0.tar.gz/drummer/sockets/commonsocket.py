# -*- coding: utf-8 -*-
import socket
from drummer.errors import Errors

class CommonSocket():

    def __init__(self, config):

        # Create TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # load configuration
        socket_config = config.get('socket')

        hostname = socket_config.get('address')
        port = socket_config.get('port')

        server_address = (hostname, port)

        max_connections = socket_config.get('max_connections')
        MSG_LEN = socket_config.get('message_len')

        # set socket objects
        self.server_address = server_address
        self.max_connections = max_connections
        self.MSG_LEN = MSG_LEN

    def receive_data(self, connection):

        MSG_LEN = self.MSG_LEN

        data = b''
        bytes_received = 0

        while bytes_received < MSG_LEN:

            chunk = connection.recv(MSG_LEN)

            bytes_received += len(chunk)

            if chunk == b'':
                raise ConnectionError(Errors.E0203)

            data += chunk

        return data
