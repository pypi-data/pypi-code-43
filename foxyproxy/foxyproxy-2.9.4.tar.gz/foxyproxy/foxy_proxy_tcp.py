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
 Written by Smart Arcs <support@smartarchitects.co.uk>, May 2018
"""
import logging
import multiprocessing
import socket
import sys
import time
from threading import Thread
import traceback
# noinspection PyCompatibility
from queue import Empty

from foxyproxy.constant import Constant
from foxyproxy.client_thread import ClientThread
from foxyproxy.csp import BaseCryptoService, ClientResult,\
    TokenRecord, ClientWork, WorkerRecord, WorkerMap, ReaderRecord

__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'


class FoxyProxyTCP(Thread):
    """
    Request processing for TCP requests
    """
    PROXY_PORT = 4001

    # create locks for smartcards
    CSP_LOCKS = {}  # dict[multiprocessing.Lock]
    WORKERS = WorkerMap()

    def __init__(self, downstream_port, signer, stop_event):
        super(FoxyProxyTCP, self).__init__()
        self.downstream_port = downstream_port
        self.signer = signer  # type: BaseCryptoService
        self.stop_event = stop_event

    def run(self):
        """
        Main loop
        """
        FoxyProxyTCP.start_server(self.downstream_port, self.signer, self.stop_event)

    @classmethod
    def start_server(cls, downstream_port, signer, stop_event):
        """
        we start one monitoring thread, while the main thread will start spawning TCP upstream threads
        when the monitoring thread detects restart of the RESTful upstream, it will load all certificates from connected
        smart-cards, these are needed for requests coming from jsignpdf - SIGN - where responses consist of
        a list of certificates and a result of signing.

        :param downstream_port: the port for the FoxyProxy server
        :type downstream_port: int
        :param signer: an instance of a subclass derived from BaseCryptoService
        :type signer: BaseCryptoService
        :param stop_event
        :type stop_event: multiprocessing.Event
        """

        if downstream_port is None or downstream_port == 0:
            downstream_port = FoxyProxyTCP.PROXY_PORT

        bound = False
        tries = 20
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # MAC
        # TCP_KEEPALIVE = 0x10
        # soc.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        # soc.setsockopt(socket.IPPROTO_TCP, TCP_KEEPALIVE, 20)

        # Linux
        # soc.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        # soc.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)  # after_idle_sec
        # soc.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)  # interval_sec
        # soc.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)  # max_fails

        logging.debug('FoxyProxy TCP listening socket created')

        while tries > 0 and not bound:
            try:
                soc.bind(('', downstream_port))
                logging.info('FoxyProxy socket bind complete. host:{0}, port:{1}'.
                             format("*", downstream_port))
                bound = True
            except socket.error as msg:
                logging.error('FoxyProxy bind failed. Error Code : %s' % str(msg))
                soc.close()
                tries -= 1
                time.sleep(5)
                soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if not bound:
            logging.error("The port %d is used by another process" % downstream_port)
            sys.exit()

        # Start listening on socket
        soc.listen(128)  # default somaxconn
        logging.info('TCP API of FoxyProxy is up and running, listening on port %d' % downstream_port)

        # get the result queue from the WORKERS map
        request_results = FoxyProxyTCP.WORKERS.result_queue

        # now keep talking with the client
        _stopping = False
        while (not stop_event.is_set()) and (not _stopping):
            # wait to accept a connection - blocking call
            try:
                # read updates from connections
                read_updates = True
                while read_updates:
                    # noinspection PyBroadException
                    try:
                        result = request_results.get(block=False)  # type: ClientResult
                        if result is not None:
                            if not result.response_sent:
                                if len(result.response) > 0:
                                    # noinspection PyBroadException
                                    try:
                                        result.connection.sendall(result.response[0])
                                        # Terminate connection for given client (if outside loop)
                                        result.connection.shutdown(socket.SHUT_RDWR)
                                        result.connection.close()
                                    except BaseException:
                                        pass
                                result.connection.shutdown(socket.SHUT_RDWR)
                                result.connection.close()
                            if result.type == ClientResult.TYPE_PIN:
                                # update the state of the smartcard
                                for each in signer.storage.cert_names:  # type: TokenRecord
                                    if result.reader == each.reader:
                                        each.pin = result.pin
                                        each.file_id = result.file_id
                            elif result.type == ClientResult.TYPE_LAST_READER:
                                signer.storage.last_enum_reader = result.last_enum_id
                            elif result.type == ClientResult.TYPE_PRIORITY:
                                signer.storage.last_priority = result.last_priority
                                signer.storage.max_enum_readers = result.max_readers
                                for key, value in signer.storage.certificates.items():  # type: str, ReaderRecord
                                    if key in result.priority_dict:
                                        value.priority = result.priority_dict[key]
                                        logging.debug("Updating priority for reader %s to %d,"
                                                      " last priority: %d, max readerd: %d"
                                                      % (key, result.priority_dict[key],
                                                         signer.storage.last_priority,
                                                         signer.storage.max_enum_readers))

                            # release the lock
                            if result.process_id >= 0:
                                FoxyProxyTCP.CSP_LOCKS[result.process_id].release()
                                logging.debug("Unlocked - %d" % result.process_id)

                            logging.debug('Client thread (%d) update received - case 0 ' % result.process_id)
                        else:
                            read_updates = False
                    except Exception:
                        read_updates = False
                conn = None
                while conn is None and (not stop_event.is_set()) and (not _stopping):
                    try:
                        soc.settimeout(0.5)  # we need to interrupt waiting
                        conn, addr = soc.accept()
                    except socket.timeout:
                        # if we run out of the thread budget, get some back
                        try:
                            read_results = True
                            while read_results:
                                # this throws exception when the queue is empty
                                result = request_results.get(block=False)  # type: ClientResult
                                if result is not None:
                                    if result.type == ClientResult.TYPE_PIN:
                                        # update the state of the smartcard
                                        for each in signer.storage.cert_names:  # type: TokenRecord
                                            if result.reader == each.reader:
                                                each.pin = result.pin
                                                each.file_id = result.file_id
                                    elif result.type == ClientResult.TYPE_LAST_READER:
                                        signer.storage.last_enum_reader = result.last_enum_id
                                    elif result.type == ClientResult.TYPE_PRIORITY:
                                        signer.storage.last_priority = result.last_priority
                                        signer.storage.max_enum_readers = result.max_readers
                                        for key, value in signer.storage.certificates.items():  # type: str,ReaderRecord
                                            if key in result.priority_dict:
                                                value.priority = result.priority_dict[key]
                                                logging.debug("Updating priority for reader %s to %d,"
                                                              " last priority: %d, max readerd: %d"
                                                              % (key, result.priority_dict[key],
                                                                 signer.storage.last_priority,
                                                                 signer.storage.max_enum_readers))
                                    if result.process_id >= 0:
                                        FoxyProxyTCP.CSP_LOCKS[result.process_id].release()
                                        logging.debug("Unlocked - %d" % result.process_id)
                                logging.debug('Client thread (%d) result received - case 1' % result.process_id)
                        except Empty:
                            pass

                if conn is None:
                    continue

                # noinspection PyUnboundLocalVariable
                ip, port = str(addr[0]), str(addr[1])
                logging.debug('A new connection from {0}:{1}'.format(ip, port))

                # signer.process_updates()
                # Identify the smartcard, select the Lock and worker

                work = ClientThread.read_request(conn, "tcp")  # type: ClientWork

                if work is not None:
                    new_lock = None  # type: multiprocessing.Lock
                    # noinspection PyTypeChecker
                    new_client = None
                    # we need to lock the smartcard so that it is not accessed twice

                    reader_index = ClientThread.find_csp_index(work, signer, FoxyProxyTCP.WORKERS.map)

                    if reader_index >= 0:
                        new_lock = FoxyProxyTCP.CSP_LOCKS[reader_index]  # type: multiprocessing.Lock
                        new_client = FoxyProxyTCP.WORKERS.workers[reader_index]  # type: WorkerRecord

                    if (new_lock is not None) and (new_client is not None):
                        # we send the new work into the work queue
                        # then we check that the process is alive in a cycle with checking for a confirmation

                        # this must be inside the worker
                        # # get the lock so only one request per card at any time
                        # logging.debug("Ready to lock - %d" % reader_index)
                        # new_lock.acquire()
                        # logging.debug("Locked - %d" % reader_index)
                        new_client.work.put(work)
                        logging.debug("Request sent to a worker, waiting for ACK: %s" % work.real_reader_name)
                        confirmed = False

                        while not confirmed:
                            # noinspection PyTypeChecker
                            ack_cmd = None
                            try:
                                ack_cmd = new_client.ack.get(timeout=0.1)  # type: ClientResult
                            except Exception as ex:
                                logging.error("No Response from the ack queue: %s" % str(ex))
                                pass
                            finally:
                                if ack_cmd is not None:
                                    if ack_cmd != ClientResult.TYPE_ACK:
                                        logging.error("Worker sent not ACK: type=%d" % ack_cmd)
                                        confirmed = True
                                    else:
                                        confirmed = True
                                        logging.debug("Worker sent ACK: type=%d" % ack_cmd)
                                else:
                                    # it expired, let's create a new one
                                    logging.debug("Worker is terminated - restarting it: %s" % work.real_reader_name)
                                    FoxyProxyTCP.WORKERS.workers_running_lock[reader_index].acquire()
                                    try:
                                        if not (FoxyProxyTCP.WORKERS.workers_running[reader_index] and
                                                FoxyProxyTCP.WORKERS.workers[reader_index].worker.is_alive()):
                                            if FoxyProxyTCP.WORKERS.workers_running[reader_index]:
                                                FoxyProxyTCP.WORKERS.workers[reader_index].worker.join(0.1)

                                            FoxyProxyTCP.WORKERS.workers[reader_index].worker = \
                                                ClientThread.create_new_worker(signer,
                                                                               work.real_reader_name, new_client.work,
                                                                               new_client.result, new_client.ack,
                                                                               new_client.rest, new_client.internal,
                                                                               reader_index,
                                                                               FoxyProxyTCP.CSP_LOCKS[reader_index])
                                            FoxyProxyTCP.WORKERS.workers_running[reader_index] = time.time()
                                            new_client = FoxyProxyTCP.WORKERS.workers[reader_index]
                                            logging.info("New client_thread created: %s" % work.real_reader_name)
                                        else:
                                            logging.info("New client_thread created by someone else: %s (info: %d)"
                                                         % (work.real_reader_name, FoxyProxyTCP.WORKERS.workers_running[reader_index]))
                                    except Exception as ex:
                                        logging.error("Exception creating new client_thread (rest): %s" % str(ex))
                                    finally:
                                        FoxyProxyTCP.WORKERS.workers_running_lock[reader_index].release()

                            pass
                    else:
                        # noinspection PyBroadException
                        try:
                            work.connection.sendall(Constant.CMD_READER_NOT_FOUND.encode())
                            work.connection.shutdown(socket.SHUT_RDWR)
                            work.connection.close()
                        except BaseException:
                            pass
                        pass
            except BaseException as ex:
                tb = "; ".join(traceback.format_exc(3).splitlines())
                logging.warning("Exception in accept: {0} ({1}), stopping event: {2}"
                                .format(str(ex), tb, stop_event.is_set()))
                if stop_event.is_set():
                    _stopping = True
                    sys.stderr.write("TCP exception - signal caught\n")
                else:
                    sys.stderr.write("TCP exception - code\n")

        # soc.close()  #  unreachable
