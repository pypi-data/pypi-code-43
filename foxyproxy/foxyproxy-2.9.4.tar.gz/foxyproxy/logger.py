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
 Written by Dan Cvrcek <support@smartarchitects.co.uk>, May 2018
"""
import hashlib
import json
import os
import pickle
import platform
# import resource
import sys
import threading
import time
import traceback
import socket
from multiprocessing import Queue
from threading import Lock

from logbook import NOTSET
from logbook.handlers import Handler
import logbook


__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'


# noinspection PyPep8Naming,PyBroadException
class logger(object):
    """
    The available logging levels are
    CRITICAL = 15  ... we use this for "usage" so we can trace actual database updates
    ERROR = 14  – for errors that occur, but are handled
    WARNING = 13  – for exceptional circumstances that might not be errors
    NOTICE = 12 – for non-error messages you usually want to see
    INFO = 11 – for messages you usually don’t want to see
    DEBUG = 10 – for debug messages
    TRACE = 9 - temporary
    """

    log_codes = {}  # a dictionary, values are tuples of int:code and str:message
    filename = None
    last_code = 0  # we will always start from 0
    code_gap = []
    file_lock = threading.Lock()
    msg_id = 1

    # create a mapping table -
    @classmethod
    def load_codes(cls, filename=None):
        """
        Load error message codes from backup file
        :param filename:
        :return:
        """
        if cls.filename is not None:
            return  # repeated call
        if filename:
            cls.filename = filename
        if cls.filename and os.path.isfile(cls.filename):
            file_cache = open(cls.filename, "rb")
            try:
                cls.log_codes = pickle.load(file_cache)
            except Exception:
                # file format is bad - fix it
                cls.log_codes = {}
                os.rename(cls.filename, cls.filename + '.corrupted %d' % int(time.time()))
                cls.update_codes()

            # lets' get all the values
            existing_codes = [a[0] for a in list(cls.log_codes.values())]
            existing_codes.sort()
            cls.code_gap = []
            if len(existing_codes) > 0:  # and find gaps we can re-use
                cls.last_code = existing_codes[-1]
                # store unused code values
                for i in range(1, cls.last_code + 1):
                    if i not in existing_codes:
                        cls.code_gap.append(i)
            else:
                pass
        elif cls.filename:
            directory = os.path.dirname(cls.filename)
            os.makedirs(directory, exist_ok=True)
            open(cls.filename, 'a').close()
            cls.log_codes = {}
            cls.update_codes()  # create a pickle file for empty dictionary
        else:
            cls.log_codes = {}
            pass

    @classmethod
    def update_codes(cls):
        """
        Update error codes
        :return:
        """
        if cls.filename is None:
            return
        file_cache = open(cls.filename+"_new", "wb")
        pickle.dump(cls.log_codes, file_cache)
        file_cache.close()
        os.remove(cls.filename)
        os.rename(cls.filename+"_new", cls.filename)

    @classmethod
    def get_code(cls, level, key, msg=None):
        """
        Get a code for a given message
        :param level:
        :param key:
        :param msg:
        :return:
        """

        key = None
        if key:
            if key in cls.log_codes:
                code = cls.log_codes[key][0]
            else:
                if len(cls.code_gap) > 0:
                    code = cls.code_gap.pop(0)
                    cls.log_codes[key] = (code, msg)
                else:
                    while cls.last_code + 1 in cls.log_codes:
                        cls.last_code += 1
                    cls.last_code += 1
                    cls.log_codes[key] = (cls.last_code, msg)
                    code = cls.last_code

                cls.file_lock.acquire()
                try:
                    cls.update_codes()
                finally:
                    cls.file_lock.release()
            result = "%s%04d" % (level[:3], code)
        else:
            code = "____"
            result = "%s%s" % (level[:3], code)

        if msg is None:
            try:
                raise Exception
            except Exception:
                tb = "; ".join(traceback.extract_stack().format())
                logger.error('Null message passed to logger',
                             name=threading.current_thread().name, traceback=tb)
        cls.file_lock.acquire()
        _id = cls.msg_id  # counter of log messages generated during this run - a simple counter
        cls.msg_id += 1
        cls.file_lock.release()
        return result, _id

    @classmethod
    def get_hash(cls, args):
        """
        Compute a hash value for the first of the arguments
        :param args:
        :return:
        """
        if len(args) > 0:
            return hashlib.sha1(args[0].encode()).hexdigest()
        else:
            return None

    @classmethod
    def get_msg_details(cls, msg, dict_params):
        """
        Get details for submitting a log message.
        :param msg:
        :param dict_params:
        :return:
        """
        key = cls.get_hash(msg)

        params = "{}"
        try:
            params = json.dumps(dict_params)
        except Exception:
            sys.stderr.out("Can't parse this %s %s\n" % (msg[0], dict_params))
            pass
        finally:
            if dict_params is not None and 'traceback' in dict_params:
                del dict_params['traceback']

        return key, params

    @classmethod
    def trace(cls, *args, **kwargs):
        """
        Trace level message
        :param args:
        :param kwargs:
        :return:
        """
        key, params = cls.get_msg_details(args, kwargs)
        try:
            logbook.trace(*args, code=key, usage=False, params=params)
        except Exception:
            pass

    @classmethod
    def debug(cls, *args, **kwargs):
        """
        debug level message
        :param args:
        :param kwargs:
        :return:
        """
        key, params = cls.get_msg_details(args, kwargs)
        try:
            logbook.debug(*args, code=key, usage=False, params=params)
        except Exception:
            pass

    @classmethod
    def info(cls, *args, **kwargs):
        """
        Info level message
        :param args:
        :param kwargs:
        :return:
        """
        key, params = cls.get_msg_details(args, kwargs)
        try:
            logbook.info(*args, code=key, usage=False, params=params)
        except Exception:
            pass

    @classmethod
    def notice(cls, *args, **kwargs):
        """
        notice level message
        :param args:
        :param kwargs:
        :return:
        """
        key, params = cls.get_msg_details(args, kwargs)
        try:
            logbook.notice(*args, code=key, usage=False, params=params)
        except Exception:
            pass

    @classmethod
    def warn(cls, *args, **kwargs):
        """
        warning level message
        :param args:
        :param kwargs:
        :return:
        """
        key, params = cls.get_msg_details(args, kwargs)
        try:
            logbook.warn(*args, code=key, usage=False, params=params)
        except Exception:
            pass

    @classmethod
    def warning(cls, *args, **kwargs):
        """
        warning level message
        :param args:
        :param kwargs:
        :return:
        """
        key, params = cls.get_msg_details(args, kwargs)
        try:
            logbook.warning(*args, code=key, usage=False, params=params)
        except Exception:
            pass

    @classmethod
    def error(cls, *args, **kwargs):
        """
        error level message
        :param args:
        :param kwargs:
        :return:
        """
        key, params = cls.get_msg_details(args, kwargs)
        try:
            logbook.error(*args, code=key, usage=False, params=params)
        except Exception:
            pass

    @classmethod
    def usage(cls, *args, **kwargs):
        """
        We use "critical" so it's always logged!
        :param args:
        :param kwargs:
        :return: None
        """
        key, params = cls.get_msg_details(args, kwargs)
        try:
            logbook.critical(*args, code=key, usage=True, params=params)
        except Exception:
            pass


class TCPHandler(Handler):
    """A custom handler using sock file or TCP sockets on a given port. It's been created from Redis Handler

    It publishes each record as json dump.

    Example setup::

        handler = TCPHandler('http://127.0.0.1', port='9200', key='redis')

    If your Redis instance is password protected, you can securely connect
    passing your password when creating a RedisHandler object.

    Example::

        handler = RedisHandler(password='your_redis_password')

    More info about the default buffer size: wp.me/p3tYJu-3b
    """
    def __init__(self, sock='logbook.sock', ip=None, port=None,
                 extra_fields=None, flush_threshold=128, flush_time=1,
                 level=NOTSET, _filter=None, bubble=True):
        Handler.__init__(self, level, _filter, bubble)

        if ip is None:
            self.sock_type = socket.AF_UNIX
            self.sock_address = sock

        else:
            self.sock_type = socket.AF_INET
            self.sock_address = (ip, port)

        self.sock = socket.socket(self.sock_type)
        self.log_counter = 0

        connected = False
        while not connected:
            try:
                self.sock.connect(self.sock_address)
                connected = True
                self.sock.close()
            except Exception as ex:
                sys.stderr.write("INFO: Logging server not available (%s)\n" % str(ex))
                sys.stderr.flush()
                time.sleep(2)

        self.extra_fields = extra_fields or {}
        self.flush_threshold = flush_threshold
        self.queue = Queue()
        self.last_error_time = time.time()
        self.lock = Lock()

        # Set up a thread that flushes the queue every specified seconds
        self._stop_event = threading.Event()
        self._flushing_t = threading.Thread(target=self._flush_task, args=(flush_time, True))
        self._flushing_t.daemon = True
        self._flushing_t.name = "Log flush"
        # self._flush_buffer()
        self._flushing_t.start()

    # noinspection PyUnusedLocal
    def _flush_task(self, wait_time, dummy):
        """Calls the method _flush_buffer every certain time.
        """
        while not self._stop_event.isSet():
            with self.lock:
                self._flush_buffer()
            self._stop_event.wait(wait_time)

    def _flush_buffer(self):
        """Flushes the messaging queue into Redis.

        All values are pushed at once for the same key.

        The method rpush/lpush is defined by push_method argument
        """
        if self.queue:
            new_socket = socket.socket(self.sock_type)
            try:
                connected = False
                while not self.queue.empty():
                    message = self.queue.get()
                    message += os.linesep
                    if not connected:
                        new_socket.connect(self.sock_address)
                        connected = True
                    new_socket.sendall(message.encode())
            except Exception as ex:
                if time.time() - self.last_error_time > 1:
                    self.last_error_time = time.time()
                    sys.stderr.write("Error connecting to log dispatcher %s\n" % str(ex))
                    sys.stderr.flush()
            finally:
                # noinspection PyBroadException
                try:
                    if new_socket is not None:
                        new_socket.close()
                except Exception:
                    pass

    def disable_buffering(self):
        """Disables buffering.

        If called, every single message will be directly pushed to Redis.
        """
        self._stop_event.set()
        self.flush_threshold = 1

    def emit(self, record):
        """Emits a pair (key, value) to redis.

        The key is the one provided when creating the handler, or redis if none
        was provided. The value contains both the message and the hostname.
        Extra values are also appended to the message.
        """
        # print("XXXXX emit")
        with self.lock:
            r = {"message": record.msg,
                 "host": platform.node(),
                 "level": record.level_name,
                 "time": record.time.isoformat()}
            r.update(self.extra_fields)
            r.update(record.kwargs)
            self.queue.put(json.dumps(r))
            self.log_counter += 1
            if self.log_counter >= self.flush_threshold:
                self.log_counter = 0
                self._flush_buffer()

    def close(self):
        """
        Flush the log bugger
        :return:
        """
        self._flush_buffer()
