#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
***
Module: FoxyProxyREST - RESTful API with Flask
***

 Copyright (C) Smart Arcs Ltd, registered in the United Kingdom.
 This file is owned exclusively by Smart Arcs Ltd.
 Unauthorized copying of this file, via any medium is strictly prohibited
 Proprietary and confidential
 Written by Smart Arcs <support@smartarchitects.co.uk>, May 2018
"""
import base64
import time

__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'

import datetime
from multiprocessing import Queue, Lock
import logging
import os
import string
import threading
import json
import random
import traceback
from waitress import serve
from flask import Flask, jsonify, request, abort
from flask_sslify import SSLify
# from flask_socketio import emit as ws_emit
from functools import wraps
from foxyproxy.client_thread import ClientThread
from foxyproxy.csp import ClientWork, WorkerRecord, ClientResult, WorkerMap, ReaderRecord

logger = logging.getLogger(__name__)

PAYLOAD_ENC_TYPE = 'AES-256-GCM-SHA256'


class AugmentedRequest(object):
    """
    Augmented request object with metadata
    """

    def __init__(self, req=None):
        self.req = req
        self.s = None  # session
        self.api_key = None
        self.ip = None
        self.last_results = None


# noinspection PyShadowingNames
class FoxyProxyREST(object):
    """
    Main server object
    """
    HTTP_PORT = 4443
    API_HEADER = 'X-Auth-API'
    CSP_LOCKS = {}
    WORKERS = WorkerMap()

    def __init__(self, signer, downstream_port=0, key_folder=None):
        self.running = True
        self.run_thread = None
        self.stop_event = threading.Event()
        self.local_data = threading.local()

        self.queue_out = Queue()
        self.queue_in = Queue()
        self.working_thread = None
        self.debug = False
        self.server = None
        self.config = None
        self.db = None

        self.flask = Flask(__name__)
        self.flask.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
        self.socket_io = None

        if downstream_port == 0:
            self.port = FoxyProxyREST.HTTP_PORT
        else:
            self.port = downstream_port
        self.key_folder = key_folder
        self.signer = signer

    #
    # Management
    #
    # noinspection PyMethodMayBeStatic
    def shutdown_server(self):
        """
        Shutdown flask server
        :return:
        """
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    def terminating(self):
        """
        Set state to terminating
        :return:
        """
        self.running = False
        self.stop_event.set()

    # noinspection PyMethodMayBeStatic
    def wsgi_options(self):
        """
        Returns kwargs for wsgi server
        :return:
        """
        kwargs = dict()
        return kwargs

    def init_server(self):
        """
        Initialize server
        :return:
        """
        self.flask.config['SECRET_KEY'] = FoxyProxyREST.random_alphanum(16)

        # if self.use_websockets:
        #     self.socket_io = SocketIO(self.flask, async_mode='eventlet', policy_server=False,
        #                               allow_upgrades=True, **self.wsgi_options())
        #
        #     logging.info('SocketIO wrapper %s for Flask: %s' % (self.socket_io, self.flask))

    def work(self):
        """
        Main work method for the server - accepting incoming connections.
        :return:
        """
        logging.info('REST thread started %s %s %s dbg: %s'
                     % (os.getpid(), os.getppid(), threading.current_thread().getName(), self.debug))
        try:
            self.init_server()
            self.init_rest()
            logging.info('RESTful API of FoxyProxy is up and running, listening on port %d' % self.port)

            self.serve_restful()  # this is blocking

        except Exception as e:
            logging.error('Exception: %s' % e)
            logging.error(traceback.format_exc())
        finally:
            logging.info('Terminating flask: %s' % self.flask)

        self.terminating()
        logging.info('Work loop terminated - RESTful API')

    # def serve_werkzeug(self):
    #     """
    #     Developer local server, not for production use
    #     :return:
    #     """
    #     r = self.flask.run(debug=self.debug, port=self.HTTP_PORT, threaded=True)
    #     logging.info('Started werkzeug server: %s' % r)
    #
    # def serve_eventlet(self):
    #     """
    #     Eventlet server, fast async, for production use
    #     :return:
    #     """
    #     listener = eventlet.listen(('0.0.0.0', self.HTTP_PORT))
    #     logging.info('Starting Eventlet listener %s for Flask %s' % (listener, self.flask))
    #     wsgi.server(listener, self.flask, **self.wsgi_options())

    def serve_restful(self):
        """
        Classical Flask application + websocket support, using eventlet
        :return:
        """
        logging.info('Starting RESTful API')
        app = self.flask
        serve(app, host='0.0.0.0', port=self.HTTP_PORT, ident="KeyChest Agent API", asyncore_use_poll=True)
        # self.socket_io.run(app=self.flask, host='0.0.0.0', port=self.HTTP_PORT, **self.wsgi_options())
        # while True:
        #     sleep(60)

    def setsslkeys(self):
        """
        Set flask with SSL
        """
        if self.key_folder:
            self.flask.run(
                os.path.join(self.key_folder, 'fullchain.pem'),
                os.path.join(self.key_folder, 'privkey.pem')
            )
            # noinspection PyUnusedLocal
            sslify = SSLify(self.flask)

    def start(self):
        """
        Starts serving thread
        :return:
        """

        self.setsslkeys()
        self.run_thread = threading.Thread(target=self.work, args=())
        self.run_thread.name = "RESTAPI_work"
        self.run_thread.daemon = True
        # self.run_thread.setDaemon(True)
        self.run_thread.start()

    #
    # REST interface
    #

    def init_rest(self):
        """
        Initializes rest server
        TODO: auth for dump, up, down - encrypt time token.
        :return:
        """

        @self.flask.route('/', methods=['GET'])
        def info():
            """
            Info enpdoint
            :return:
            """
            result = {
                'endpoints': [
                    '/api/v1.0/command (POST)',
                    '/api/v1.0/hello (POST, GET)',
                    '/api/v1.0/select (POST, GET)'
                    '/ws - web socket server'
                ]
            }
            return jsonify(result)

        @self.flask.route('/api/v1.0/command', methods=['POST'])
        def command():
            """
            EP handler for command
            :return:
            """
            request_in = FoxyProxyREST._process_payload(request, self.config)
            response = None
            try:
                work = ClientThread.read_request(None, "rest", request_in)  # type: ClientWork
                if work is None:
                    return jsonify({})
                reader_index = ClientThread.find_csp_index(work, self.signer, FoxyProxyREST.WORKERS.map)
                if reader_index >= 0:
                    new_lock = FoxyProxyREST.CSP_LOCKS[reader_index]  # type: Lock
                    new_client = FoxyProxyREST.WORKERS.workers[reader_index]  # type: WorkerRecord

                    if (new_lock is not None) and (new_client is not None):
                        # we send the new work into the work queue
                        # then we check that the process is alive in a cycle with checking for a confirmation

                        # # get the lock so only one request per card at any time
                        # logging.debug("Ready to lock - %d (REST)" % reader_index)
                        # new_lock.acquire()
                        # logging.debug("Locked - %d (REST)" % reader_index)

                        work.alt_result_queue = True
                        new_client.work.put(work)
                        confirmed = False

                        while not confirmed:
                            # noinspection PyTypeChecker
                            ack_cmd = None
                            # noinspection PyBroadException
                            try:
                                ack_cmd = new_client.ack.get(timeout=0.1)  # type: ClientResult
                            except Exception:
                                pass
                            finally:
                                if ack_cmd is not None:
                                    if ack_cmd != ClientResult.TYPE_ACK:
                                        logging.error("Worker sent not ACK: type=%d (REST)", ack_cmd.type)
                                        confirmed = True
                                    else:
                                        confirmed = True
                                elif not new_client.worker.is_alive():
                                    # it expired, let's create a new one
                                    logging.debug("Worker is terminated - restarting (rest): %s"
                                                  % work.real_reader_name)
                                    FoxyProxyREST.WORKERS.workers_running_lock[reader_index].acquire()
                                    try:
                                        if not (FoxyProxyREST.WORKERS.workers_running[reader_index] and
                                                FoxyProxyREST.WORKERS.workers[reader_index].worker.is_alive()):
                                            if FoxyProxyREST.WORKERS.workers_running[reader_index]:
                                                FoxyProxyREST.WORKERS.workers[reader_index].worker.join(0.1)
                                            FoxyProxyREST.WORKERS.workers[reader_index].worker = \
                                                ClientThread.create_new_worker(self.signer, work.real_reader_name,
                                                                               new_client.work, new_client.result,
                                                                               new_client.ack, new_client.rest,
                                                                               new_client.internal,
                                                                               reader_index,
                                                                               FoxyProxyREST.CSP_LOCKS[reader_index])
                                            FoxyProxyREST.WORKERS.workers_running[reader_index] = time.time()
                                            new_client = FoxyProxyREST.WORKERS.workers[reader_index]
                                            logging.info("New client_thread created (rest): %s"
                                                         % work.real_reader_name)
                                        else:
                                            logging.info("New client_thread created by someone else (rest): %s"
                                                         % work.real_reader_name)
                                    except Exception as ex:
                                        logging.error("Exception creating new client_thread (rest): %s" % str(ex))
                                    finally:
                                        FoxyProxyREST.WORKERS.workers_running_lock[reader_index].release()
                            pass

                        # noinspection PyTypeChecker
                        result = None
                        # noinspection PyBroadException
                        try:
                            result = new_client.rest.get(timeout=200)  # max time for processing = 200 seconds
                        except Exception:
                            pass
                        finally:
                            new_lock.release()
                            logging.debug("Unlocked (rest - command) - %d" % result.process_id)
                            if result is None:
                                logging.error("REST response is None: %s" % json.dumps(request_in))
                                return jsonify(response)
                            else:
                                return jsonify(result.response)

            except Exception as ex:
                logging.error("Exception in REST command method: %s", str(ex))
                return jsonify(response)
                pass

        @self.flask.route('/api/v1.0/select/<name>', methods=['GET'])
        @self.flask.route('/api/v1.0/select/<name>/<limit>', methods=['GET'])
        def terminal(name, limit=1):
            """
            The parameter is just one 'name' ...v1.0/terminal?name=xxxx . It returns a JSON with an ordered
            list of terminals
            :return:
            """
            terminal_name = name
            # noinspection PyBroadException
            # try:
            #     terminal_name = request.args.get('name')
            # except Exception:
            #     pass
            try:
                _limit = int(limit)
                if _limit < 0:
                    _limit = 0

                reader_index = 0
                new_lock = FoxyProxyREST.CSP_LOCKS[reader_index]  # type: Lock
                new_client = FoxyProxyREST.WORKERS.workers[reader_index]  # type: WorkerRecord

                if (new_lock is not None) and (new_client is not None):
                    # we send the new work into the work queue
                    # then we check that the process is alive in a cycle with checking for a confirmation

                    # # get the lock so only one request per card at any time
                    # logging.debug("Ready to lock - %d (REST)" % reader_index)
                    # new_lock.acquire()
                    # logging.debug("Locked - %d (REST)" % reader_index)
                    work = ClientWork()
                    work.command = ClientWork.CMD_SELECT_TERM
                    work.alt_result_queue = True
                    # byte array for base64, result back to str
                    work.req_reader = base64.b64encode(terminal_name.strip().encode()).decode() + '|' + str(_limit)
                    new_client.work.put(work)
                    confirmed = False

                    while not confirmed:
                        # noinspection PyTypeChecker
                        ack_cmd = None
                        # noinspection PyBroadException
                        try:
                            ack_cmd = new_client.ack.get(timeout=0.1)  # type: ClientResult
                        except Exception:
                            pass
                        finally:
                            if ack_cmd is not None:
                                if ack_cmd != ClientResult.TYPE_ACK:
                                    logging.error("Worker sent not ACK: type=%d (REST)", ack_cmd.type)
                                    confirmed = True
                                else:
                                    confirmed = True
                            else:
                                # it expired, let's create a new one
                                logging.debug("Worker is terminated - restarting (rest2): %s" % work.real_reader_name)
                                FoxyProxyREST.WORKERS.workers_running_lock[reader_index].acquire()
                                try:
                                    if not (FoxyProxyREST.WORKERS.workers_running[reader_index] and
                                            FoxyProxyREST.WORKERS.workers[reader_index].worker.is_alive()):
                                        if FoxyProxyREST.WORKERS.workers_running[reader_index]:
                                            FoxyProxyREST.WORKERS.workers[reader_index].worker.join(0.1)
                                        FoxyProxyREST.WORKERS.workers[reader_index].worker = \
                                            ClientThread.create_new_worker(self.signer, work.real_reader_name,
                                                                           new_client.work, new_client.result,
                                                                           new_client.ack, new_client.rest,
                                                                           new_client.internal,
                                                                           reader_index,
                                                                           FoxyProxyREST.CSP_LOCKS[reader_index])
                                        FoxyProxyREST.WORKERS.workers_running[reader_index] = time.time()
                                        new_client = FoxyProxyREST.WORKERS.workers[reader_index]
                                        logging.info("New client_thread created (rest2): %s"
                                                     % work.real_reader_name)
                                    else:
                                        logging.info("New client_thread created by someone else (rest2): %s"
                                                     % work.real_reader_name)
                                except Exception as ex:
                                    logging.error("Exception creating new client_thread (rest): %s" % str(ex))
                                finally:
                                    FoxyProxyREST.WORKERS.workers_running_lock[reader_index].release()
                        pass

                    # noinspection PyTypeChecker
                    result = None
                    # noinspection PyBroadException
                    try:
                        result = new_client.rest.get(timeout=200)  # type: ClientResult  # max time  = 200 seconds

                        if result.type != ClientResult.TYPE_PRIORITY:
                            logging.error("Reader select result is incorrect type: %d" % result.type)
                        self.signer.storage.last_priority = result.last_priority
                        self.signer.storage.max_enum_readers = result.max_readers
                        returned_results = len(result.priority_dict)
                        found = 0
                        list_of_set = []
                        for key, value in self.signer.storage.certificates.items():  # type: str, ReaderRecord
                            if key in result.priority_dict:
                                found += 1
                                self.signer.storage.certificates[key].priority = result.priority_dict[key]
                                list_of_set.append(key)
                                logging.debug("Updating priority for reader %s to %d,"
                                              " last priority: %d, max readers: %d"
                                              % (key, self.signer.storage.certificates[key].priority,
                                                 self.signer.storage.last_priority,
                                                 self.signer.storage.max_enum_readers))
                            else:
                                logging.debug("No matching name in certificate storage %s" % key)
                        if found != returned_results:
                            logging.info("REST select - updated error; in: %s, set: %s" %
                                         (", ".join(list(result.priority_dict.keys())), ", ".join(list_of_set)))
                        logging.debug("REST Select update OK, updated results: %d", found)
                    except Exception as ex:
                        tb = "; ".join(traceback.format_exc(3).splitlines())
                        logging.error("Exception in RESET select %s, traceback: %s" % (str(ex), tb))
                        pass
                    finally:
                        new_lock.release()
                        logging.debug("Unlocked (rest - select) - %d" % result.process_id)
                        if result is None:
                            logging.error("REST response is None - select")
                            return ""
                        else:
                            return os.linesep.join(result.response)

            except Exception:
                abort("Request has an incorrect parameter 'limit'")

        @self.flask.route('/api/v1.0/select', methods=['GET'])
        def terminal2():
            """
            The parameter is just one 'name' ...v1.0/terminal?name=xxxx . It returns a JSON with an ordered
            list of terminals
            :return:
            """
            # noinspection PyBroadException
            try:
                reader_index = 0
                new_lock = FoxyProxyREST.CSP_LOCKS[reader_index]  # type: Lock
                new_client = FoxyProxyREST.WORKERS.workers[reader_index]  # type: WorkerRecord

                if (new_lock is not None) and (new_client is not None):
                    # we send the new work into the work queue
                    # then we check that the process is alive in a cycle with checking for a confirmation

                    # # get the lock so only one request per card at any time
                    # logging.debug("Ready to lock - %d (REST)" % reader_index)
                    # new_lock.acquire()
                    # logging.debug("Locked - %d (REST)" % reader_index)
                    work = ClientWork()
                    work.command = ClientWork.CMD_SELECT_TERM
                    work.alt_result_queue = True
                    # byte array for base64, result back to str
                    work.req_reader = "|0"
                    new_client.work.put(work)
                    confirmed = False

                    while not confirmed:
                        # noinspection PyTypeChecker
                        ack_cmd = None
                        # noinspection PyBroadException
                        try:
                            ack_cmd = new_client.ack.get(timeout=0.1)  # type: ClientResult
                        except Exception:
                            pass
                        finally:
                            if ack_cmd is not None:
                                if ack_cmd != ClientResult.TYPE_ACK:
                                    logging.error("Worker sent not ACK: type=%d (REST)", ack_cmd.type)
                                    confirmed = True
                                else:
                                    confirmed = True
                            else:
                                # it expired, let's create a new one
                                logging.debug("Worker is terminated - restarting (rest3): %s" % work.real_reader_name)
                                FoxyProxyREST.WORKERS.workers_running_lock[reader_index].acquire()
                                try:
                                    if not (FoxyProxyREST.WORKERS.workers_running[reader_index] and
                                            FoxyProxyREST.WORKERS.workers[reader_index].worker.is_alive()):
                                        if FoxyProxyREST.WORKERS.workers_running[reader_index]:
                                            FoxyProxyREST.WORKERS.workers[reader_index].worker.join(0.1)
                                        FoxyProxyREST.WORKERS.workers[reader_index].worker = \
                                            ClientThread.create_new_worker(self.signer, work.real_reader_name,
                                                                           new_client.work, new_client.result,
                                                                           new_client.ack, new_client.rest,
                                                                           new_client.internal,
                                                                           reader_index,
                                                                           FoxyProxyREST.CSP_LOCKS[reader_index])
                                        FoxyProxyREST.WORKERS.workers_running[reader_index] = time.time()
                                        new_client = FoxyProxyREST.WORKERS.workers[reader_index]
                                        logging.info("New client_thread created (rest3): %s"
                                                     % work.real_reader_name)
                                    else:
                                        logging.info("New client_thread created by someone else (rest3): %s"
                                                     % work.real_reader_name)
                                except Exception as ex:
                                    logging.error("Exception creating new client_thread (rest): %s" % str(ex))
                                finally:
                                    FoxyProxyREST.WORKERS.workers_running_lock[reader_index].release()
                        pass
                    # noinspection PyTypeChecker
                    result = None
                    # noinspection PyBroadException
                    try:
                        result = new_client.rest.get(timeout=10)  # type: ClientResult  # max time  = 10 seconds

                        if result.type != ClientResult.TYPE_PRIORITY:
                            logging.error("Reader select result is incorrect type: %d" % result.type)

                        if len(result.priority_dict) > 0:
                            logging.error("Reader select returns data even though no updates should be made, len = %d"
                                          % (len(result.priority_dict)))
                        logging.debug("Reader select info returned: %s" % ",".join(result.response))
                    except Exception as ex:
                        logging.error("REST select info exception %s" % str(ex))
                        pass
                    finally:
                        new_lock.release()
                        logging.debug("Unlocked (rest - select) - %d" % result.process_id)
                        if result is None:
                            logging.error("REST select - response is None")
                            return ""
                        else:
                            return os.linesep.join(result.response)

            except Exception:
                abort("Request has an incorrect parameter 'limit'")

        @self.flask.route('/api/v1.0/hello', methods=['GET'])
        def hello():
            """
            Hello EP implementation
            :return:
            """
            return self.on_keep_alive()

        @self.flask.route('/api/v1.0/hello', methods=['POST'])
        def hello_post():
            """
             Hello POST EP implementation
            :return:
            """
            return self.on_keep_alive()

        @self.flask.errorhandler(400)
        def bad_request(e):
            """
             400 hander
            :param e:
            :return:
            """
            return jsonify(error=400, text=str(e)), 400

        @self.flask.errorhandler(405)
        def method_not_allowed(e):
            """
            405 handler
            :param e:
            :return:
            """
            return jsonify(error=405, text=str(e)), 405

        @self.flask.errorhandler(500)
        def internal_server_error(e):
            """
            500 handler
            :param e:
            :return:
            """
            return jsonify(error=500, text=str(e)), 500

        @self.flask.errorhandler(404)
        def url_not_found(e):
            """
            404 handler
            :param e:
            :return:
            """
            return jsonify(error=404, text=str(e)), 404

        # @self.socket_io.on('message', namespace='/ws')
        # def handle_message(message):
        #     """
        #     WS message handler
        #     :param message:
        #     :return:
        #     """
        #     logging.info('received ws message: ' + message)
        #     request_in = FoxyProxyREST._process_payload(message, self.config)
        #     thread_object = ClientThread("ws", request_in, self.signer)
        #     thread_object.run()  # use without threading
        #     result = thread_object.get_response()
        #     ws_emit('foxyproxy', jsonify(result))
        #
        # @self.socket_io.on('connect', namespace='/ws')
        # def test_connect():
        #     """
        #     WS connect handler
        #     :return:
        #     """
        #     logging.info('WS client connected')

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def wrap_requests(*args0, **kwargs0):
        """
        Function decorator for requests call, wrapping in try-catch, catching exceptions
        :type args0: object
        :return:
        """

        def wrap_requests_decorator(*args):
            """
            Decorator
            :param args:
            :return:
            """

            f = args[0]

            @wraps(f)
            def wrapper(*args, **kwds):
                """
                response wrapper
                :param args:
                :param kwds:
                :return:
                """
                # noinspection PyBroadException
                self = args[0]
                r = None
                try:
                    r = self._auth_request(kwds.get('request', None))
                    args = list(args)[1:]
                    res = f(self, r, *args, **kwds)
                    return res

                except Exception as e:
                    logging.error('Uncaught exception: %s' % e)
                    self.trace_logger.log(e)

                finally:
                    if r is not None:
                        FoxyProxyREST.silent_close(r.s)

                # fail
                abort(500)

            return wrapper

        return wrap_requests_decorator

    @staticmethod
    def silent_close(c, quiet=True):
        # noinspection PyBroadException
        """

        :param c:
        :param quiet:
        :return:
        """
        try:
            if c is not None:
                c.close()
        except Exception as e:
            if not quiet:
                logging.error('Close exception: %s' % e)
        pass

    @staticmethod
    def _process_payload(_request, config):
        """
        Decrypts payload, fails request in case of a problem
        :param _request:
        :return:
        """
        if _request is None:
            logging.debug('Invalid request')
            abort(400)

        json_in = _request.get_json(force=True)
        if json_in is None or 'data' not in json_in:
            logging.warning('Invalid request')
            abort(400)

        data = _request.json['data']
        js = FoxyProxyREST.unprotect_payload(data, config)

        return js

    #
    # Handlers
    #
    # noinspection PyUnusedLocal
    @staticmethod
    def on_keep_alive(request=None):
        """
        Simple keepalive
        :param request:
        :return:
        """
        return jsonify({'result': True})

    @staticmethod
    def jsonify(obj):
        """
        Transforms object for transmission
        :param obj:
        :return:
        """
        if obj is None:
            return obj
        elif isinstance(obj, list):
            return [jsonify(x) for x in obj]
        elif isinstance(obj, dict):
            return {str(k): jsonify(obj[k]) for k in obj}
        elif isinstance(obj, datetime.datetime):
            return FoxyProxyREST.unix_time(obj)
        elif isinstance(obj, datetime.timedelta):
            return obj.total_seconds()
        else:
            return obj

    @staticmethod
    def unix_time(dt):
        """
        Get a unix_time regardless of the timezone
        :param dt:
        :return:
        """
        if dt is None:
            return None
        cur = datetime.datetime.utcfromtimestamp(0)
        if dt.tzinfo is not None:
            cur.replace(tzinfo=dt.tzinfo)
        else:
            cur.replace(tzinfo=None)
        # noinspection PyBroadException
        try:
            return (dt - cur).total_seconds()
        except Exception:
            pass

    @staticmethod
    def random_alphanum(length):
        """
        Generates a random password which consists of digits, lowercase and uppercase characters
        :param length:
        :return:
        """
        return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(length))

    @staticmethod
    def unprotect_payload(payload, config):
        """
        Processes protected request payload
        :param payload:
        :param config:
        :return:
        """
        if payload is None:
            raise ValueError('payload is None')
        if ('enctype' in payload) and (config is None):
            raise ValueError('encryption config is None')

        if 'enctype' in payload:
            if payload['enctype'] != PAYLOAD_ENC_TYPE:
                raise ValueError('Unknown payload protection: %s' % payload['enctype'])
            else:
                plaintext = ""
                # TODO encryption - probably not needed
                # key = make_key(config.vpnauth_enc_password)
                # iv = base64.b64decode(payload['iv'])
                # tag = base64.b64decode(payload['tag'])
                # ciphertext = base64.b64decode(payload['payload'])
                # plaintext = decrypt(key=key, iv=iv, ciphertext=ciphertext, tag=tag)
                js = json.loads(plaintext)
        else:
            js = payload

        return js
