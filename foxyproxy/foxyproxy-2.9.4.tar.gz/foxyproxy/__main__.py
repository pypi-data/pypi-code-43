# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
***
Module: foxyproxy - CloudFoxy proxy - TCP proxy for flexible access to CloudFoxy RESTful API
***

# Copyright (C) Smart Arcs Ltd registered in the United Kingdom.
# Unauthorized copying of this file, via any medium is strictly prohibited
#
# This file is provided under a license as specified in the "LICENSE" file, which is part
# of this software package.
#
# Written by Smart Arcs <support@smartarchitects.co.uk>, August 2018
"""
import multiprocessing
import signal
import sys
# import socket
# import threading
# import time

# import logbook
# import logging
import getopt
import os
import threading
import time
from multiprocessing import Queue

from foxyproxy.client_thread import ClientThread

from foxyproxy.beacon_thread import BeaconThread
from foxyproxy.foxy_proxy_tcp import FoxyProxyTCP
from foxyproxy.foxy_proxy_rest import FoxyProxyREST
from foxyproxy.csp import Register, WorkerRecord, WorkerMap, ClientWork
from foxyproxy.queue_handler import QueueHandler
from foxyproxy.version import proxy_version
# from log_dispatcher import LogDispatcher
# from foxyproxy.logger import TCPHandler
import logging

__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Beta'

logger = logging.getLogger()
# logging.basicConfig(level=logging.DEBUG)
logger.setLevel(logging.INFO)
# ch = logging.StreamHandler()
ch = QueueHandler()
fmt = logging.Formatter('%(asctime)s - %(name)s(Q) - %(levelname)s - %(message)s')
ch.setFormatter(fmt)
ch.setLevel(logging.INFO)
logger.addHandler(ch)

beacon_thread = None  # not running yet
# coloredlogs.install(level='INFO', logger=logger)
# logging.basicConfig(level=logging.DEBUG)


main_stop = multiprocessing.Event()
parent_group_pid = None


def print_help():
    """
    A simple help printing
    """
    print("foxyproxy, version %s. (c) Smart Arcs Ltd. Visit https://gitlab.com/cloudfoxy .\n\n"
          "The proxy accepts the following parameters:" % proxy_version)
    print("  -h, --help - this help, if present it will stop the process\n")
    print("  -l  <DEBUG|ERROR|WARNING|INFO> - minimum level to log, default is INFO")
    print("  -r, --register - will attempt to create certification request(s)\n")
    print("  -p <port>, --port <port> - port where the proxy listens, 4001 if not set\n")
    print("  -p2 <port>, --port2 <port> - port where proxy's RESTful and WS server listens, 4443 if not set\n")
    print("  -k <path>, --keys <path> - location of keys for downstream RESTfull HTTPS (folder must contain files ")
    print("        'privkey.pem' and 'fullchain.pem' files in LetsEncrypt format; if not present, HTTP only\n")
    print("  -s http(s)://<url:port>|file://<path>|python://dummy> - address of the upstream server, e.g., ")
    print("        FoxyRest - http://upstream.cloudfoxy.com:8081 ; 'python://' will use an internal simulator\n")
    print("  -c <signer>, --signer <signer> - identification of the signature provider; currently supported are "
          "\"ICA\", \"PGP\"\n")
    print("  -t <token>, --token <token> - authorization token / API key for the signing API")


# def setup_logging(level=logbook.DEBUG, true_socket=False):
#     """
#
#     :param level:
#     :param true_socket:
#     :return:
#     """
#
#     if true_socket:
#         local_sock = socket.gethostbyname("localhost")
#         port = 44444
#         _handler = TCPHandler(None, flush_threshold=1, flush_time=0, ip=local_sock, port=port,
#                               extra_fields={}, level=level)
#     else:
#         sock_file = os.path.join('/etc/foxyproxy/logbook.sock')
#         _handler = TCPHandler(sock_file, flush_threshold=1, flush_time=0,
#                               extra_fields={}, level=level)
#     # noinspection PyBroadException
#     try:
#         _handler.pop_application()
#     except BaseException:
#         pass
#     _handler.push_application()


# noinspection PyUnusedLocal
def signal_handler(sig, frame):
    """
    Signal handler
    :param sig:
    :param frame:
    :return:
    """
    global beacon_thread
    global logger
    global ch
    global main_stop  # type: multiprocessing.Event()

    main_stop.set()
    beacon_thread.stopnow()
    ch.close()
    sys.stderr.write("Waiting 1 second to exit\n")
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    time.sleep(1)
    # if parent_group_pid is not None:
    #     os.killpg(parent_group_pid, signal.SIGINT)

    raise SystemExit('Terminating FoxyProxy')  # this is supposed to kill main()


def process_watch(workers):
    """
    A simple process watch function that will try to close worker processes that died
    :return:
    """

    re_raise = False
    while True:
        time.sleep(10)
        workers.instance_lock.acquire()
        logging.debug("watcher run started at %d" % int(time.time()))
        # noinspection PyBroadException
        try:
            temp_dict = {'system': 0}
            for each_reader in {**workers.map, **temp_dict}:
                if each_reader == 'system':
                    _status_index = 0
                else:
                    _status_index = workers.map[each_reader]
                workers.workers_running_lock[_status_index].acquire()
                re_raise = False
                # noinspection PyBroadException
                try:
                    if workers.workers_running[_status_index]:
                        if not workers.workers[_status_index].worker.is_alive():
                            # noinspection PyBroadException
                            try:
                                workers.workers[_status_index].worker.join(0.1)
                                if not workers.workers[_status_index].worker.is_alive():
                                    workers.workers_running[_status_index] = 0
                                    logging.debug("Worker process joined after termination, reader: %s"
                                                  % each_reader)
                                else:
                                    logging.error("Worker termination failed in process_watch, reader: %s"
                                                  % each_reader)
                            except Exception as ex:
                                logging.error("Worker process died / terminated but join failed, reader: %s, reason: %s"
                                              % (each_reader, str(ex)))
                except Exception as ex:
                    logging.error("Terminating main watch method: cause %s" % str(ex))
                finally:
                    workers.workers_running_lock[_status_index].release()
        except Exception:
            pass
        finally:
            workers.instance_lock.release()
            logging.debug("watch run finished at %d" % int(time.time()))
            if re_raise:
                raise Exception("terminating process_watch")


def main():
    """
    Main entry function
    """

    global beacon_thread
    global ch

    # noinspection PyBroadException
    try:
        signal.signal(signal.SIGINT, signal_handler)
    except Exception:
        pass
    # noinspection PyBroadException
    try:
        signal.signal(signal.SIGTERM, signal_handler)
    except Exception:
        pass

    # noinspection PyUnusedLocal
    foxyproxy_port = None
    upstream_server = None
    token = None
    register = False
    key_folder = None  # if none, RESTful will be HTTP only
    signer_name = 'ica'
    foxyproxy_port = 0
    foxyproxy_port2 = 0
    # log_level = logbook.DEBUG
    log_level = logging.INFO

    if len(sys.argv) > 1:
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'hrp:s:t:c:l:',
                                       ['help', 'register', 'port=', 'server=', 'signer=', 'token=', 'level='])
        except getopt.GetoptError:
            # print help information and exit:
            print_help()
            print("You provided %s" % ' '.join(sys.argv[1:]))
            ch.close()
            sys.exit(2)

        for o, a in opts:
            if o in ('-h', '--help'):
                print_help()
                ch.close()
                sys.exit(0)
            else:
                if o in ('-r', '--register'):
                    register = True
                if o in ('-p', '--port'):
                    if a.isdigit():
                        foxyproxy_port = int(a)
                    else:
                        print("Invalid value of the port, it has to be a number")
                if o in ('-l', '--level'):
                    _a = ("%s" % a).lower()
                    if _a == 'debug':
                        log_level = logging.DEBUG
                    elif _a == 'info':
                        log_level = logging.INFO
                    elif _a == 'error':
                        log_level = logging.ERROR
                    elif _a == 'warning':
                        log_level = logging.WARNING

                if o in ('-p2', '--port2'):
                    if a.isdigit():
                        foxyproxy_port2 = int(a)
                    else:
                        print("Invalid value of the port2, it has to be a number")
                if o in ('-s', '--server'):
                    upstream_server = a.strip()
                if o in ('-c', '--signer'):
                    signer_name = a.strip().lower()
                if o in ('-t', '--token'):
                    token = a.strip()
                if o in ('-k', '-keys'):
                    key_folder = a.strip()

    # alternative logbook logging
    # log_dispatcher_thread = LogDispatcher(logger_stop_event, ip="127.0.0.1")
    # log_dispatcher_thread.name = "LogDispatcher"
    # log_dispatcher_thread.start()

    # setup_logging(log_level, true_socket=True)  # alternative logbook logging
    logger.setLevel(log_level)

    upstream_test = upstream_server.lower().split('://')
    if (((len(upstream_test) < 2) and (upstream_test[0] != 'python'))
        or ((upstream_test[0] != 'file') and (upstream_test[0] != 'http')
            and (upstream_test[0] != 'https'))) and (upstream_test[0] != 'python'):
        print("Upstream signer must start with 'file://' or 'http://' or 'https://' or 'python")
        exit(-1)

    if (foxyproxy_port == foxyproxy_port2) and foxyproxy_port > 0:
        print("port and port2 must be different")
        exit(-1)
    if upstream_test[0] == 'file':
        # let's try to open the file
        file_path = upstream_test[1]
        if not os.path.isfile(file_path):
            print("Can't open the local signer %s" % file_path)
            exit(-1)
        if not os.access(file_path, os.R_OK):
            print("The local signer %s is not readable" % file_path)
            exit(-1)

    # create a manager to share data between processes and to allow update - e.g., last PIN used
    # process_manager = Manager()  # throws errors on connections probably due to gevent present in the project

    cmd_line = dict(upstream=upstream_server, signer=signer_name, token=token, register=register)

    # create an instance of the signing service according to the CLI parameters, default is:
    #  'ica', http://localhost:8081, token='b'
    signer = Register.get_service(cmd_line)

    # create worker threads and locks - we assume 120 CSPs max
    # first create LOCKS for smartcards
    locks = {}
    workers = WorkerMap()
    result_queue = Queue()
    workers.result_queue = result_queue
    for i in range(0, workers.CAPACITY + 1):  # one for "virtual", 120 for physical
        locks[i] = multiprocessing.Lock()
        q_work = Queue()
        q_result = result_queue
        q_ack = Queue()
        q_rest = Queue()
        q_internal = Queue()
        new_worker = WorkerRecord()
        new_worker.work = q_work
        new_worker.result = q_result
        new_worker.ack = q_ack
        new_worker.internal = q_internal
        new_worker.rest = q_rest
        new_worker.worker = ClientThread(signer, new_worker.work, new_worker.result, new_worker.ack, new_worker.rest,
                                         new_worker.internal, i, locks[i])
        workers.workers[i] = new_worker
        workers.workers_running[i] = 0
        workers.workers_running_lock[i] = threading.Lock()

    # let's start checking the status of the upstream server - it works even when the upstream is just a
    # local command
    BeaconThread.WORKERS = workers
    beacon_thread = BeaconThread(signer)
    beacon_thread.name = "BeaconThread"
    beacon_thread.start()

    while not signer.server.is_up():
        time.sleep(0.1)

    if not register:
        # and we finally start the proxy itself to accept client requests

        # TCP server
        FoxyProxyTCP.CSP_LOCKS = locks
        FoxyProxyTCP.WORKERS = workers
        tcpapi = FoxyProxyTCP(downstream_port=foxyproxy_port, signer=signer, stop_event=main_stop)
        tcpapi.name = "TCPAPI"
        tcpapi.start()

        # RESTful API
        FoxyProxyREST.CSP_LOCKS = locks
        FoxyProxyREST.WORKERS = workers
        restful = FoxyProxyREST(signer, downstream_port=foxyproxy_port, key_folder=key_folder)
        restful.name = "RESTAPI"
        restful.setsslkeys()
        restful_thread = threading.Thread(target=restful.work)
        restful_thread.name = 'REST API - control'
        restful_thread.start()

        process_watch(workers)  # blocking

        logging.info("Terminating with %d client processes" % len(workers.workers))
        for _csp in workers.workers:  # type: WorkerRecord
            csp = workers.workers[_csp]  # type
            kill_cmd = ClientWork()
            kill_cmd.command = ClientWork.CMD_KILL
            if csp.worker.is_alive():
                sys.stderr.write("Sending KILL to %s\n" % csp.worker.name)
                csp.work.put(kill_cmd)
                # noinspection PyBroadException
                try:
                    csp.ack.get(timeout=0.05)
                except Exception:
                    if csp.worker.is_alive():
                        sys.stderr.write("ERROR - Can't stop a worker %s\n" % csp.worker.name)

        sys.stderr.write("INFO - FoxyProxyTCP done\n")


if __name__ == '__main__':
    # os.setpgrp()  # create new process group, become its leader
    # parent_group_pid = os.getpgid(multiprocessing.current_process().pid)
    try:
        main()
        sys.stderr.write("FoxyProxy terminated\n")
        sys.stderr.flush()
    finally:
        # this is now in the signal handler
        # os.killpg(0, signal.SIGKILL)  # kill all processes in my group
        pass
