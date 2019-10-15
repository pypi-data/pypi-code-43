#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
***
Module:
***

 Copyright (C) Smart Arcs Ltd, registered in the United Kingdom.
 This file is owned exclusively by Smart Arcs Ltd.
 Unauthorized copying of this file, via any medium is strictly prohibited
 Proprietary and confidential
"""
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'

import json
import os
import socket
import sys
import threading
from datetime import datetime
from time import time, sleep
import traceback
from foxyproxy.logger import logger


class LogDispatcher(threading.Thread):
    """
    Writing multi-processing logs to a file
    """

    def __init__(self, stop_event, sock_file='logbook.sock', ip=None, port=44444, to_file=False):
        """
        :param stop_event:
        :param sock_file: the TCP .sock file for listening
        :param ip: or we can listen on an interface and ...
        :param port: ... tcp port
        """

        super(LogDispatcher, self).__init__()
        self.stopping = False
        self.messages = []
        self.stop_event = stop_event  # type: threading.Event
        self.stopped = False
        self.to_file = to_file

        if ip is not None:
            self.sock_address = (ip, port)
            self.sock_type = socket.AF_INET
        else:
            self.sock_type = socket.AF_UNIX
            self.sock_address = "/etc/foxyproxy/logbook.sock"
            # first we need to create a .sock file for internal communication
            try:
                os.unlink(self.sock_address)
            except OSError:
                if os.path.exists(self.sock_address):
                    raise

        self.code_dir = '/etc/keychest_agent/log_codes.pickle'
        # first, let's empty the queue
        self.myindex = None

    def tcp_server(self):
        """
        This is internal TCP  server for logging - it listens on localhost
        :return:
        """

        while True:
            serv_socket = socket.socket(self.sock_type, socket.SOCK_STREAM)

            tries = 20
            bound = False
            while tries > 0 and not bound:
                try:
                    serv_socket.bind(self.sock_address)
                    sys.stderr.write('Logging socket listening.' + os.linesep)
                    sys.stderr.flush()

                    bound = True
                except socket.error as msg:
                    sys.stderr.write('Cannot bind to logging socket: %s' % str(msg) + os.linesep)
                    sys.stderr.flush()
                    tries -= 1
                    sleep(5)

            if not bound:
                serv_socket.close()
                continue
            try:
                serv_socket.listen(1)
                while True:
                    # Wait for a connection
                    connection, client_address = serv_socket.accept()
                    end_of_data = False
                    data = ""
                    try:
                        while not end_of_data:
                            data += connection.recv(10000).decode()  # type: str
                            if data:
                                # process data - look for end of line
                                _lines = data.split(os.linesep)
                                # if data ends with os.linesep -> list item will be empty string
                                length = 0
                                for _line in _lines:
                                    length = len(_line)
                                    if length > 0:
                                        self.messages.append(_line)
                                if length > 0:
                                    data = _lines[len(_lines) - 1]  # store the last one
                                else:
                                    data = ''
                            else:
                                # no more data
                                end_of_data = True
                    finally:
                        connection.close()
            except Exception as ex:
                tb = "; ".join(traceback.format_exc(3).splitlines())
                sys.stderr.write("Exception in listening to logging port %s - %s" % (str(ex), tb) + os.linesep)
                sys.stderr.flush()
            finally:
                serv_socket.close()
                sleep(5)

    def run(self):
        """

        :return:
        """

        # first we need to start the TCP server to accept logs
        tcp_server = threading.Thread(target=self.tcp_server, args=())
        tcp_server.name = "TCPHandler"
        tcp_server.daemon = True  # let it terminate with the main thread
        tcp_server.start()
        log_directory = '/var/log/foxyproxy'

        # logger.load_codes(self.code_dir)
        # noinspection PyUnusedLocal
        last_submit = time()
        # noinspection PyUnusedLocal
        upload_string = []  # this would be "" for splunk!
        # last_reconnect = time()
        # noinspection PyUnusedLocal
        usage_logs_counter = 0
        # noinspection PyUnusedLocal
        last_config_test = time()
        if self.to_file:
            log_filename = datetime.now().strftime("foxyproxy_%Y_%m_%d.log")
            log_file = open(os.path.join(log_directory, log_filename), 'a')

        while True:
            # noinspection PyBroadException
            try:
                if len(self.messages) > 0:
                    record = self.messages.pop(0)  # take the oldest message
                    skip = False
                    # noinspection PyBroadException
                    try:
                        raw = json.loads(record)
                        level = raw['level'].upper()
                        # flag whether it's a trace or usage log message
                        if 'usage' in raw:
                            usage = raw['usage']
                        else:
                            usage = False
                        if usage:
                            level = 'USE'
                            skip = False

                        if 'params' in raw:
                            params = raw['params']
                        else:
                            params = "{}"

                        if 'code' in raw:
                            code, msg_id = logger.get_code(level, raw['code'], raw['message'])
                        else:
                            code, msg_id = logger.get_code(level, None, raw['message'])

                        _time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
                        _params = json.loads(params)
                        if len(self.messages) > 50:
                            _params['backlog'] = len(self.messages)
                        _message = {'time': raw['time'][:19],
                                    'event':
                                        {
                                            'level': level,
                                            'code': code,
                                            'message': raw['message'],
                                            'params': _params,
                                            'process': raw['process'],
                                            'id': msg_id,
                                            'host': raw['host'],
                                            'usage': usage,
                                            'log_time': _time,
                                        }
                                    }
                        message = json.dumps(_message) + os.linesep

                        # local log
                        # if self.to_file:
                        #     name_now = datetime.now().strftime("agent_%Y_%m_%d.log")
                        #     # a new day - delete files older than 30 days
                        #     if name_now != log_filename:
                        #         log_filename = name_now
                        #         log_file.close()
                        #         log_file = open(os.path.join(log_directory, log_filename), 'a')
                        #         _, _, files = next(os.walk(log_directory))
                        #         to_delete = len(files) - 30
                        #         while to_delete > 0:
                        #             to_delete -= 1
                        #             name = files.pop(0)
                        #             # noinspection PyBroadException
                        #             try:
                        #                 os.remove(os.path.join(log_directory, name))
                        #             except:
                        #                 pass
                        #
                        #     log_file.write(message)
                        #     log_file.flush()
                        #     pass
                        # else:
                        sys.stdout.write(message)
                        sys.stdout.flush()

                    except Exception:
                        pass
                else:  # i.e., the queue is empty
                    sleep(2.0)
                    if self.stop_event.is_set():
                        break
            except Exception as ex:
                sys.stderr.write("Exception " + str(ex))
                pass
        # noinspection PyUnreachableCode
        sys.stderr.write("Terminating log dispatcher" + os.linesep)
        self.stopped = True

    def stop(self):
        self.stop_event.set()
        while not self.stopped:
            sleep(0.5)
