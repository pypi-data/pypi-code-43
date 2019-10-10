#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import socket
import zeropy.proto as proto
import zeropy.protoutil as proto_manager


class SocketManager(object):
    host = '127.0.0.1'
    port = 38100

    sock_timeout = 100
    connected = False
    proto = None
    response = None
    need_notify = False
    counter = 5
    def __init__(self):
        self.create_socket()

    def __del__(self):
        self.disconnect()

    def create_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.sock_timeout is not None:
            self.sock.settimeout(self.sock_timeout)

    def connect(self, host=None, port=None):
        if host is not None:
            self.host = host
        if port is not None:
            self.port = port
        server_address = (self.host, self.port)
        try:
            self.sock.connect(server_address)
            self.connected = True
            self.counter = 5
        except ConnectionRefusedError:
            logging.error('connection was refused')
            self.__reconnect()

        except socket.timeout:
            logging.warning('socket timeout')
            self.__reconnect()

    def disconnect(self):
        if self.connected:
            self.sock.close()

    def is_connected(self):
        if self.connected:
            return True
        logging.error("is_connected: no connection")
        return False

    def __reconnect(self):
        import time
        time.sleep(1)
        logging.warning('try reconnect')
        self.counter -= 1
        if self.counter > 0:
            self.create_socket()
            self.connect(self.host, self.port)


    def __send_data(self):
        send_status = False
        while send_status is False:
            try:
                self.sock.sendall(self.proto.buffer.raw)
                req_term = proto.TerminatingBlock()
                req_term.pack()
                self.sock.sendall(req_term.buffer.raw)
                send_status = True
            except ConnectionResetError:
                logging.error('reset by peer, close app')
                import sys
                sys.exit('critical error')
            except socket.timeout:
                logging.error('socket is timeout')
                self.create_socket()
                if self.counter > 0:
                    self.connect(self.host, self.port)
                self.counter -= 1

    def __recvall(self, nbytes):
        data = b''
        while len(data) < nbytes:
            packet = self.sock.recv(nbytes - len(data))
            if not packet:
                return None
            data += packet
        return data

    def __recv(self, p_type, term_block):
        print('zeropy:socket_manager - try to recv cmd')
        recv_status = False
        while recv_status is False:
            try:
                if p_type is proto.CMD_NUMS['SendBuffer'] \
                        or p_type is proto.CMD_NUMS['SendTransaction']:
                    return

                self.response = proto.Header()
                if self.response.buf_size() is not 0:
                    self.sock.recv_into(self.response.buffer,
                                        self.response.buf_size())
                self.response.unpack()
                print('got responce cmd', self.response.cmd_num)
                data = None
                if p_type is proto.CMD_NUMS['GetBuffer'] or p_type is proto.CMD_NUMS['GetBufferPart']:
                    buffer = self.__recvall(self.response.size)
                    if type is proto.CMD_NUMS['GetBuffer']:
                        import zeropy.utils as utils
                        if utils.check_crc32_sum(buffer) is not True:
                            print('crc32 sum no equal')
                            return
                    data = buffer
                else:
                    data = proto_manager.create_struct(p_type)
                    if data is None:
                        return
                    self.sock.recv_into(data.buffer,
                                            data.buf_size())
                    data.unpack()

                recv_status = True
                if term_block is True:
                    resp_block = proto.TerminatingBlock()
                    self.sock.recv_into(resp_block.buffer,
                                        resp_block.buf_size())
                    resp_block.unpack()

                return data
            except ConnectionResetError:
                logging.error('reset by peer, close app')
                import sys
                sys.exit('critical error')
            # except socket.error as err:
            #         recv_status = False
            #         print(err.errno)
            #         self.connected = False

    def recv_into(self, _type):
        result = proto_manager.recv_proto(_type)
        recv_status = False
        while recv_status is False:
            try:
                self.sock.recv_into(result.buffer,
                                    result.buf_size())
                result.unpack()
                recv_status = True
            except ConnectionResetError:
                logging.error('reset by peer, close app')
                import sys
                sys.exit('critical error')

        return result

    def method(self, *argc, _type, term_block):
        self.proto = proto_manager.create_proto(*argc, type=_type)

        if self.proto is None:
            return None

        self.__send_data()
        result = self.__recv(_type, term_block)

        return result

