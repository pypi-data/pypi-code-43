#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2018,2019 Aljoscha Pörtner
# Copyright 2019 André Kirsch
# This file is part of SwarmRob.
#
# SwarmRob is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SwarmRob is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SwarmRob.  If not, see <https://www.gnu.org/licenses/>.

import socketserver
import logging
import logging.handlers
import os
import struct
import sys
import threading

import pickle

from ..utils import network

MAX_BYTE_SIZE_FOR_LOG_ROTATING = 100000
FILE_COUNT_FOR_LOG_ROTATING = 5
SWARM_LOGFILE_PATH = "/var/tmp/swarmlogs/"


class LogRecordStreamHandler(socketserver.StreamRequestHandler):
    """
    Handles the streaming logging requests of the workers
    """

    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            print("Remote log message received")
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = pickle.loads(chunk)
            record = logging.makeLogRecord(obj)
            print(record)
            self.handle_log_record(record)

    def handle_log_record(self, record):
        """
            Handles an incoming log record and passes it to the classic logger
        :param record: record that should be logged
        :return:
        """
        # if a name is specified, we use the named logger rather than the one
        # implied by the record.
        log_filename = SWARM_LOGFILE_PATH + str(record.swarm_uuid) + '.out'

        # Set up a specific logger with our desired output level
        logger = logging.getLogger('MyLogger')
        logger.setLevel(logging.DEBUG)

        # Add the log message handler to the logger
        handler = logging.handlers.RotatingFileHandler(
                log_filename, maxBytes=MAX_BYTE_SIZE_FOR_LOG_ROTATING, backupCount=FILE_COUNT_FOR_LOG_ROTATING)
        formatter = logging.Formatter(
                '%(swarm_uuid)s %(worker_uuid)s %(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        # N.B. EVERY record gets logged. This is because Logger.handle
        # is normally called AFTER logger-level filtering. If you want
        # to do filtering, do it at the client end to save wasting
        # cycles and network bandwidth!
        logger.handle(record)


class LogRecordSocketReceiver(socketserver.ThreadingTCPServer):
    """
    Simple TCP socket-based logging receiver
    """
    allow_reuse_address = 1

    def __init__(self, host='localhost',
                 port=0,
                 handler=LogRecordStreamHandler):
        socketserver.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 1

    def serve_until_stopped(self):
        """
        Serves the TCP logging server until break
        """

        import select
        while not self.abort:
            rd, _, _ = select.select([self.socket.fileno()], [], [], self.timeout)
            if rd:
                self.handle_request()


class RemoteLoggingServer(threading.Thread):
    """
    Wrapper class for the actual remote logging server
    """
    def __init__(self, interface=None):
        if not os.path.exists(SWARM_LOGFILE_PATH):
            os.makedirs(SWARM_LOGFILE_PATH)
        network_info = network.NetworkInfo(interface)
        self.interface = network_info.interface
        self.tcp_server = LogRecordSocketReceiver(host=network_info.ip_address)
        self.hostname = self.tcp_server.socket.getsockname()[0]
        self.port = self.tcp_server.socket.getsockname()[1]
        threading.Thread.__init__(self)

    def run(self):
        """
        Start the remote logging server and run until interrupt
        """
        try:
            self.tcp_server.serve_until_stopped()
        except KeyboardInterrupt:
            self.tcp_server.abort = 1
            sys.exit(0)
