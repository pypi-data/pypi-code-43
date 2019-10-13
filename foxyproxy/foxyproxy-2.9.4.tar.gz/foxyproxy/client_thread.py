#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
***
Module: client_thread - Implementation of the proxy request processing
***
"""

# Copyright (C) Smart Arcs Ltd, Enigma Bridge Ltd, registered in the United Kingdom.
# Unauthorized copying of this file, via any medium is strictly prohibited
#
# This file is provided under a license as specified in the "LICENSE" file, which is part
# of this software package.
#
# Written by Smart Arcs <support@smartarchitects.co.uk>, August 2018
import base64
import json
import logging
import sys
import threading
import time
import traceback
from socket import SHUT_RDWR
from multiprocessing import Process, Queue
# from threading import Thread
from foxyproxy.csp import ClientResult, ClientWork
from foxyproxy.constant import Constant
from foxyproxy.csp import BaseCryptoService, TokenRecord
from foxyproxy.request_data import RequestData

__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'


logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# logger.addHandler(ch)
# fh = logging.FileHandler('foxyproxy.log')
# fh.setLevel(logging.INFO)
# logger.addHandler(fh)


class ClientThread(Process):
    """
    Function for handling connections. This will be used to create threads
    """

    MAX_UPTIME = 600  # uptime not more than 600
    MAX_COUNTER_RUNS = 500  # maximum number of requests to process
    REACTION_TIME = 5  # how long till we re-check the status

    def __init__(self, signer, queue_in, queue_out, queue_ack, queue_rest, queue_internal, _id, mylock=None):
        """
        We need a way to make this re-entrant and also to kill itself when:
        1. the parent process died
        2. when it ran for more than X minutes
        3. when it processed more than Y requests

        :param signer: reference of the signer
        :type signer: BaseCryptoService
        :param queue_in - requests
        :type queue_in: Queue
        :param queue_out - results
        :type queue_out: Queue
        # :param token_info
        # :type token_info: TokenRecord
        :param _id: id of the process / upstream crypto provider
        """
        super(ClientThread, self).__init__()
        self.connection = None
        self.signer = signer
        self.protocol = None
        self.response = ""
        self.upstreamsession = self.signer.getupstreamconnection()
        self.req_commands = []
        self.req_reader = None
        self.req_password = None
        self.queue_in = queue_in  # type: Queue
        self.queue_out = queue_out  # type: Queue
        self.queue_ack = queue_ack  # type: Queue
        self.queue_rest = queue_rest  # type: Queue
        self.internal_jobs = queue_internal  # type: Queue
        self.alt_result_queue = False
        self.mylock = mylock
        self.id = _id
        self.real_reader = TokenRecord()
        self.real_reader_name = None
        self.start_time = time.time()
        self.watcher_running = True
        self.main_running = True
        self.run_counter = 0
        self.queued_counter = 0
        # noinspection PyTypeChecker
        self.sync_back = None  # type: ClientResult

    @classmethod
    def read_request(cls, connection, protocol, data_in=None):
        """
        This will read the incoming request and identify the reader
        :param data_in:
        :param protocol:
        :param connection
        :type connection: sockets.socket
        """

        create_work = ClientWork()
        create_work.command = ClientWork.CMD_PROCESS
        create_work.connection = connection
        create_work.protocol = protocol
        if create_work.protocol == 'tcp':
            result = ClientThread._read_tcp(create_work)
        else:
            result = ClientThread._read_service(create_work, data_in)

        if not result:
            connection.shutdown(SHUT_RDWR)
            connection.close()
            return None
        if create_work.req_reader:
            create_work.reader_name = create_work.req_reader
            create_work.real_reader_name = BaseCryptoService.decode_cf_reader(create_work.req_reader)
            if len(create_work.real_reader_name) < 1:
                create_work.real_reader_name = None
        else:
            create_work.real_reader_name = None

        return create_work

    @classmethod
    def create_new_worker(cls, signer, name, work_q, result_q, ack_q, ack_rest, internal_q, index, mylock=None):
        """
        A simple creation of a new worker process. The caller must acquire the Lock!!
        :param signer:
        :param name:
        :param work_q:
        :param result_q:
        :param ack_q:
        :param ack_rest:
        :param internal_q:
        :param index:
        :param mylock:
        :return:
        """

        # it expired, let's create a new one
        new_client = ClientThread(signer, work_q, result_q, ack_q, ack_rest, internal_q, index, mylock)
        new_client.daemon = True
        if name is None:
            _reader_name = "csp_worker_proxy"
        else:
            _reader_name = name
        new_client.name = "csp_worker_" + _reader_name
        logging.debug("Created a new worker process for %s" % _reader_name)
        new_client.start()
        return new_client

    @classmethod
    def find_csp_index(cls, work, signer, name_map):
        """
        Takes a name and finds the CSP matching that name
        :param work:
        :param signer:
        :param name_map:
        :return:
        """
        reader_index = -1  # invalid value
        if work.real_reader_name is None:
            # proxy will serve without upstream CSPs - ENUM, LIST, etc
            reader_index = 0
        elif work.real_reader_name in name_map:
            reader_index = name_map[work.real_reader_name]
        else:
            # it may be a name -> let's try to get
            # only of the first commands is SIGN or CHAIN
            set_new_name = False
            if len(work.req_commands) > 0:
                if work.req_commands[0]['name'] in ['CHAIN', 'SIGN']:
                    _name = signer.get_token(work.reader_name)  # type: list
                    logging.debug("Name transformation - chain / sign: %s" % work.reader_name)
                    if (len(_name) == 1) and (_name[0].reader in name_map):  # get  record and extract the reader name
                        _reader = _name[0]  # type: TokenRecord
                        work.real_reader_name = _reader.reader
                        set_new_name = True
                        reader_index = name_map[work.real_reader_name]
                    else:
                        logging.error("Name transformation failed, %s found %d reader(s)"
                                      % (work.real_reader_name, len(_name)))
            if not set_new_name:
                work.real_reader_name = None  # make sure it's None
                reader_index = -1
        return reader_index

    def serve_work_queue(self, internal_jobs, serve_work_queue_stop):
        """
        A simple method / thread that will check work queue and store jobs
        :param serve_work_queue_stop
        :type serve_work_queue_stop: threading.Event
        :return:
        """

        while not serve_work_queue_stop.is_set():  # safe stopping of the feeder
            # noinspection PyBroadException
            try:
                new_work = self.queue_in.get(timeout=ClientThread.REACTION_TIME)  # type: ClientWork
                if new_work is not None:  # type: ClientWork
                    # send back an ACK
                    self.queue_ack.put(ClientResult.TYPE_ACK)
                    self.queued_counter += 1
                    # noinspection PyBroadException
                    try:
                        if new_work.command == ClientWork.CMD_KILL:
                            sys.stderr.write("KILL: waiting for internal queue to empty: %s" % self.name)
                            logging.info("KILL: waiting for internal queue to empty: %s" % self.name)
                            # empty the queue - we want to terminate
                            while not internal_jobs.empty():
                                time.sleep(0.1)
                                internal_jobs.get(block=False)
                            sys.stderr.write("KILL: internal queue empty - shutdown: %s" % self.name)
                            logging.info("KILL: internal queue empty - shutdown: %s" % self.name)
                    except Exception:
                        pass
                    finally:
                        internal_jobs.put(new_work)
                        logging.debug("Queue length for ID: %d is %d (total queued: %d, running time: %d)"
                                      % (self.id, self.queued_counter - self.run_counter, self.queued_counter,
                                         time.time() - self.start_time))
            except Exception:
                # it can be timeout or anything else
                pass
            finally:
                if self.time_is_up():
                    serve_work_queue_stop.set()
                pass
                # _time = time.time() - self.start_time
                # logging.debug("Ping on client thread %s - uptime %d, requests %d"
                #               % (self.name, _time, self.run_counter))
        logging.info("Internal work queue client stopped: %s" % self.name)

    def job_processing(self, no_wait=False):
        """
        One command serving method
        :return: boolean - whether to continue
        :rtype: bool
        """

        keep_running = True

        # noinspection PyBroadException
        try:
            if no_wait:
                new_work = self.internal_jobs.get(timeout=1)  # type: ClientWork
            else:
                new_work = self.internal_jobs.get(timeout=ClientThread.REACTION_TIME)  # type: ClientWork
            self.run_counter += 1
            if new_work is not None:  # type: ClientWork
                if new_work.command == ClientWork.CMD_KILL:
                    logging.info("KILL command received internally: %s" % self.name)
                    keep_running = False
                elif new_work.command == ClientWork.CMD_SELECT_TERM:
                    if self.mylock is None:
                        logging.debug("No lock, continuing - %d" % self.id)
                    else:
                        logging.debug("Ready to lock (rest) - %d" % self.id)
                        self.mylock.acquire()
                        logging.debug("Locked (rest) - %d" % self.id)

                    _data = new_work.req_reader.split('|')
                    self.alt_result_queue = new_work.alt_result_queue
                    if len(_data) != 2:
                        logging.error("Terminal selection - incorrect data: %s" % new_work.req_reader)
                    try:
                        _data[0] = base64.b64decode(_data[0].encode()).decode()
                        _data[1] = int(_data[1])
                        new_list, priorities, last_priority = self.signer.prioritize(_data[0], _data[1])
                        self.sync_back = ClientResult()  # type: ClientResult
                        self.sync_back.type = ClientResult.TYPE_PRIORITY
                        self.sync_back.process_id = self.id
                        self.sync_back.max_readers = _data[1]
                        self.sync_back.last_priority = last_priority
                        self.sync_back.priority_dict = priorities
                        self.sync_back.response = new_list
                        self.sync_back.response_sent = False

                        if self.alt_result_queue:
                            self.queue_rest.put(self.sync_back)
                        elif self.queue_out is not None:  # restful option
                            self.queue_out.put(self.sync_back)
                        self.sync_back = None
                        self.alt_result_queue = False
                    except Exception as ex:
                        logging.error("Terminal selection - exception %s" % str(ex))
                    finally:
                        logging.debug("Client request served - %s" % self.real_reader_name)
                elif new_work.command != ClientWork.CMD_PROCESS:
                    logging.error("Unknown request received by ClientThread: %d" % new_work.command)

                else:
                    # get the lock so only one request per card at any time
                    if self.mylock is None:
                        logging.debug("No lock, continuing - %d" % self.id)
                    else:
                        logging.debug("Ready to lock - %d" % self.id)
                        self.mylock.acquire()
                        logging.debug("Locked - %d" % self.id)
                    self.connection = new_work.connection
                    self.protocol = new_work.protocol
                    self.req_reader = new_work.req_reader
                    self.req_password = new_work.req_password
                    self.real_reader.name = new_work.real_reader_name  # lazy assignment
                    self.real_reader_name = new_work.real_reader_name
                    self.req_commands = new_work.req_commands
                    self.alt_result_queue = new_work.alt_result_queue
                    self.serve_request()
        except Exception as ex:
            if len(str(ex)) == 0:
                logging.error("Exception in job_processing: Queue Empty")
            else:
                logging.error("Exception in job_processing: %s" % str(ex))
            # it can be timeout or anything else
            keep_running = False
            pass
        return keep_running

    def time_is_up(self):
        """
        Checks if we continue accepting jobs or not
        :return:
        """
        keep_running = True
        _time = time.time() - self.start_time
        if _time > ClientThread.MAX_UPTIME:
            keep_running = False
        if self.run_counter > ClientThread.MAX_COUNTER_RUNS:
            keep_running = False

        return not keep_running

    def run(self):
        """
        Thread body - selects TCP or REST processing
        :return:
        """

        # first we start a thread that will receive jobs so we don't block the main process loop
        stop_feeder = False
        # feeder = threading.Thread(target=self.serve_work_queue, args=(lambda: stop_feeder, self.internal_jobs))
        serve_work_queue_stop = threading.Event()
        feeder = threading.Thread(target=self.serve_work_queue, args=(self.internal_jobs, serve_work_queue_stop))

        feeder.name = "Feeder_%d" % self.id
        feeder.start()
        keep_running = True
        # an infinite loop that will terminate when the process is old enough
        while not serve_work_queue_stop.is_set():
            # noinspection PyBroadException
            keep_running = self.job_processing()
            if keep_running:
                keep_running = not self.time_is_up()
            if not keep_running:
                serve_work_queue_stop.set()
            logging.debug("Ping on client thread %s - uptime %d, requests %d"
                          % (self.name, int(time.time() - self.start_time), self.run_counter))

        serve_work_queue_stop.set()
        feeder.join()  # wait for safe termination
        # if there's a final command, let's process it
        while self.job_processing(no_wait=True):
            logging.debug("last command processing")

        self.signer.closesession(self.upstreamsession)
        # let's do queue status log
        logging.debug("Emptiness of queues: queue_in %d, queue_out: %d, queue_ack: %d, queue_rest: %d, internal: %d"
                      % (self.queue_in.empty(), self.queue_out.empty(), self.queue_ack.empty(), self.queue_rest.empty(),
                         self.internal_jobs.empty()))
        logging.info("Client thread terminated %s" % self.name)

    def serve_request(self):
        """
        Processing of a single command
        """

        # lock is done by the TCP / REST threads
        self.sync_back = ClientResult()  # type: ClientResult
        if self.id is not None:
            self.sync_back.process_id = self.id

        try:
            if self.protocol == 'tcp':
                self.run_tcp()
            else:
                self.run_service()
        finally:
            logging.debug("Client request served - %s" % self.real_reader_name)

            if self.alt_result_queue:
                self.queue_rest.put(self.sync_back)
            elif self.queue_out is not None:  # restful option
                self.queue_out.put(self.sync_back)
        self.sync_back = None
        self.alt_result_queue = False
        logging.debug("ClientThread %d completed a request" % self.id)

    @classmethod
    def _read_tcp(cls, client_work):
        """
        Reads request from TCP connection
        :param client_work
        :type client_work: ClientWork
        :return:
        """

        if client_work.connection is None:
            logging.error("_read_tcp called without connection")
            return False

        more_coming = True
        client_work.req_commands = []
        client_work.req_reader = None
        empty_line = False
        data = None
        while more_coming:
            # Receiving from client
            # first we read all the commands
            # noinspection PyBroadException
            try:
                data_raw = client_work.connection.recv(4096)
            except BaseException:
                break
            except IOError:
                break
            if len(data_raw) == 0:  # connection was closed
                break
            buffer_list = None
            try:
                # buffer_list.append(data_raw)
                if buffer_list is None:
                    buffer_list = data_raw
                else:
                    buffer_list += data_raw
            except TypeError:
                logging.error("Received data can't be converted to text")
                pass

            # data = ''.join(buffer_list)
            # noinspection PyBroadException
            try:
                data = buffer_list.decode('utf-8')
            except Exception:
                data = ""

            # data = ">Simona /111.222.123.033@07|\n>2:RESET|\n>3:APDU:1100000000|\n>4:APDU:2200000000|" \
            #        "\n>5:APDU:3300000000|"
            # data = ">K|\n>3:SIGN:0000000000000000000000000000000000000000|"
            lines = data.splitlines()

            for line in lines:
                # noinspection PyBroadException
                try:
                    logging.debug("Received data: %s" % line)
                    line = line.strip()  # remove white space - beginning & end
                    if (len(line) == 0) and len(client_work.req_commands) > 0:
                        more_coming = False
                        continue
                    if line[0] == '#':
                        # this may be in internal info
                        pass
                    elif line[0] != '>':
                        # we will ignore this line
                        continue
                    line = line[1:].strip()  # ignore the '>' and strip whitespaces
                    if line.rfind('|') < 0:
                        logging.debug("Possibly missing | at the end of the line %s " % line)
                    else:
                        line = line[:line.rfind(u"|")]
                    if not client_work.req_reader:
                        cmd_parts = line.split(u':')
                        # noinspection PyUnusedLocal
                        client_work.req_reader = cmd_parts[0]  # if '|' is not in string, it will take the whole line
                        if len(cmd_parts) > 1:
                            client_work.req_password = cmd_parts[1]
                    else:
                        cmd_parts = line.split(':')
                        if len(cmd_parts) == 1:
                            client_work.req_reader = cmd_parts[0]
                            continue

                        if len(cmd_parts) < 2 or len(cmd_parts) > 4:
                            logging.error('Invalid line %s - ignoring it' % line)
                            continue

                        item = {'id': cmd_parts[0], 'name': cmd_parts[1], 'bytes': None, 'object': None}
                        if item['name'] == 'EMPTYLINE':
                            empty_line = True
                        else:
                            if len(cmd_parts) > 2:
                                item['bytes'] = cmd_parts[2]
                            if len(cmd_parts) > 3:
                                item['object'] = cmd_parts[3]
                            client_work.req_commands.append(item)
                except Exception:
                    pass
            # let's see - we have a command or more and empty_line is False => we end
            if (len(client_work.req_commands) > 0) and (not empty_line):
                more_coming = False

        if client_work.req_reader is None:
            if data is None:
                logging.error("No reader ID sent, the raw data is: None")
            else:
                logging.error("No reader ID sent, the raw data is: %s" % data)
            # time.sleep(0.1)  # sleep little before making another receive attempt
            return False
        elif len(client_work.req_commands) < 1:
            logging.error("No commands to process")
            # time.sleep(0.1)  # sleep little before making another receive attempt
            return False
        else:
            return True

    def run_tcp(self):
        """
        A TCP request processing method
        :return:
        """
        try:
            self.sync_back.response = []
            for command in self.req_commands:
                input_req = RequestData(self.req_reader,
                                        command['id'],
                                        command['name'],
                                        command['bytes'],
                                        command['object'],
                                        password=self.req_password)

                ########
                response_data = self.process_command(input_req)
                #########
                _temp_enum_id = self.signer.storage.last_enum_reader
                response = ">{0}{1}{2}{3}\n".format(input_req.command_id,
                                                    Constant.CMD_SEPARATOR,
                                                    response_data,
                                                    Constant.CMD_RESPONSE_END)

                if self.real_reader is not None:
                    self.sync_back.reader = self.real_reader.reader
                    self.sync_back.pin = self.real_reader.pin
                    self.sync_back.file_id = self.real_reader.file_id
                    self.sync_back.type = ClientResult.TYPE_PIN
                elif self.signer.storage.last_enum_reader != _temp_enum_id:
                    self.sync_back.type = ClientResult.TYPE_LAST_READER
                    self.sync_back.last_enum_id = self.signer.storage.last_enum_reader

                # noinspection PyArgumentEqualDefault
                self.response = response
                logging.debug("Response %s" % response)
            # break  # we close the connection after
        except Exception as ex:
            tb = traceback.format_exc()
            logging.info('Exception in serving response (1), ending thread - cause %s, traceback %s'
                         % (str(ex), tb))
        finally:
            self.response = self.response.encode("utf-8")
            self.connection.sendall(self.response)
            self.connection.shutdown(SHUT_RDWR)
            self.connection.close()
            self.sync_back.response.append(self.response)
            self.sync_back.response_sent = True

        # Terminate connection for given client (if outside loop)
        # noinspection PyBroadException
        try:
            self.connection.shutdown(SHUT_RDWR)
            self.connection.close()
        except BaseException:
            pass
        return

    @classmethod
    def _read_service(cls, client_work, data_in=None):
        """

        :param client_work:
        :type client_work: ClientWork
        :param data_in
        :return:
        """

        if (client_work.connection is None) and (data_in is None):
            logging.error("_read_service called without a connection set and data")
            return False
        # infinite loop so that function do not terminate and thread do not end.
        # Receiving from client
        # first we read all the commands
        data_json = None
        try:
            if data_in is not None:
                data_json = data_in
            else:
                data_json = client_work.connection

            if not data_json:  # connection was closed
                return False

            if "reader" not in data_json or (('command' not in data_json) and ('commands' not in data_json)):
                logging.debug("JSON structure is incorrect, it must have 'reader' and 'command'/'commands'")
                return False

            # JSON will have the following structure
            #  {
            #       "reader": "Simona /111.222.123.033@07",
            #       "commands": [
            #           { "nonce": "2",
            #             "line": "RESET" },
            #           { "nonce": "3",
            #             "line": "APDU:1100000000" }
            #       ],
            #       "command": {"nonce": "2",
            #                   "line": "RESET"}
            #  }

            client_work.req_reader = data_json['reader']

            if 'password' in data_json:  # this is not currently used
                client_work.req_password = data_json['password']
            else:
                client_work.req_password = None

            if ("command" in data_json) or ("commands" in data_json):
                if "command" in data_json:
                    commands = [data_json['command']]
                else:
                    commands = data_json['commands']

                for each_cmd in commands:
                    if ("id" in each_cmd) and ("line" in each_cmd):
                        cmd_id = each_cmd['id']
                        cmd_line = each_cmd['line']
                        cmd_parts = cmd_line(':')
                        if len(cmd_parts) < 1 or len(cmd_parts) > 3:
                            logging.error('Invalid line %s - ignoring it' % cmd_line)
                        else:
                            item = {'id': cmd_id, 'name': cmd_parts[0], 'bytes': None, 'object': None}
                            if len(cmd_parts) > 1:
                                item['bytes'] = cmd_parts[1]
                            if len(cmd_parts) > 2:
                                item['object'] = cmd_parts[2]
                            client_work.req_commands.append(item)
                    else:
                        logging.debug("An item in 'commands' element has a missing 'id' or 'line'")

            if len(client_work.req_commands) == 0:
                logging.error("No commands to process")
                return False
            else:
                return True
        except Exception as ex:
            if data_json:
                data_string = json.dumps(data_json)
            else:
                data_string = ""
            logging.debug("Error reading client request - service (error: %s) %s"
                          % (str(ex), data_string))
            return False

    def run_service(self):
        """
        The main service loop
        :return:
        """
        try:
            response_json = []
            for command in self.req_commands:
                input_req = RequestData(self.req_reader,
                                        command['id'],
                                        command['name'],
                                        command['bytes'],
                                        command['object'],
                                        password=self.req_password)

                ########
                response_data = self.process_command(input_req)
                #########
                one_item = {
                    "id": input_req.command_id,
                    "line": response_data
                }
                response_json.append(one_item)

                to_return = {
                    "response": response_json
                }
                self.response = to_return
                self.sync_back.response = [self.response]
                self.sync_back.response_sent = False
                logging.debug("Response is %s" % json.dumps(response_json))
        except Exception as ex:
            logging.info('Exception in serving response (2), ending thread, cause: %s' % str(ex))

        return

    def process_command(self, input_req):
        """
        Processes command that has been successfully parsed.
        :param input_req:
        :type input_req: RequestData
        :return:
        """
        logging.debug(u"Reader:'{0}',CommandID:'{1}',Command:'{2}'".
                      format(input_req.reader_name, input_req.command_id, input_req.command_name))

        processing_command = input_req.command_name.upper()

        # SEND APDU
        if processing_command == Constant.CMD_APDU:
            token_name = BaseCryptoService.decode_cf_reader(input_req.reader_name)
            response_data = self.signer.apdu(self.upstreamsession, token_name, command=input_req.command_data)
        # get CHAIN
        elif processing_command == Constant.CMD_CHAIN:
            # reader_name = Alias
            response_data = self.signer.chain(input_req.reader_name)
        # ALIAS
        elif processing_command == Constant.CMD_ALIAS:
            aliases = self.signer.aliases()
            response_data = "|".join(aliases)
        # ENUM - get names of all connected tokens
        elif processing_command == Constant.CMD_ENUM:
            readers = self.signer.tokens(input_req.reader_name, input_req.command_data)
            response_data = "|".join(readers)
        # READERS
        elif processing_command == Constant.CMD_LIST:
            readers = self.signer.get_readers(input_req.reader_name, input_req.command_data, input_req.command_object)
            response_data = "|".join(readers)
        # SIGN
        elif processing_command == Constant.CMD_SIGN:
            response_data = self.signer.sign(self.upstreamsession, input_req.reader_name, input_req.command_data,
                                             password=input_req.password)
        # RESET
        elif processing_command == Constant.CMD_RESET:
            token_name = BaseCryptoService.decode_cf_reader(input_req.reader_name)
            response_data = self.signer.reset(self.upstreamsession, token_name)

        elif processing_command == Constant.CMD_CLIENT:
            response_data = 'OK'
        else:  # No valid command found
            response_data = Constant.CMD_RESPONSE_FAIL

        return response_data

    def get_response(self):
        """
        A simple getter for response
        :return:
        """
        return self.response
