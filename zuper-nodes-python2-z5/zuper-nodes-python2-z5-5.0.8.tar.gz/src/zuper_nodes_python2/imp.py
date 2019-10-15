#!/usr/bin/env python2
from __future__ import unicode_literals

import os
import sys
import time
import traceback

import cbor2 as cbor

from . import logger
from .constants import *

# Python 2 compatibility.
try:
    TimeoutError
except NameError:
    import socket
    TimeoutError = socket.timeout

__all__ = ['wrap_direct', 'Context']


class Context:
    def info(self, s):
        pass

    def error(self, s):
        pass

    def debug(self, s):
        pass

    def warning(self, s):
        pass

    def write(self, topic, data):
        pass


# noinspection PyBroadException
def wrap_direct(agent):
    logger.info('python %s' % ".".join(map(str, sys.version_info)))
    data_in = os.environ.get('AIDONODE_DATA_IN', '/dev/stdin')
    data_out = os.environ.get('AIDONODE_DATA_OUT', '/dev/stdout')

    while not os.path.exists(data_in):
        logger.info('Waiting for %s to be created.' % data_in)
        time.sleep(1)

    if data_in == '/dev/stdin':
        f_in = sys.stdin
    else:
        f_in = open(data_in, 'rb')

    # f_in = io.BufferedReader(io.open(f_in.fileno()))
    # f_in = sys.stdin
    if data_out.startswith('fifo:'):
        data_out = data_out.lstrip('fifo:')
        os.mkfifo(data_out)

        logger.info('Opening fifo %s for writing. Will block until reader appears.' % data_out)

    f_out = open(data_out, 'wb')

    logger.info('Starting reading from %s' % data_in)

    try:
        while True:

            # whatever
            # logger.info('Reading...')
            try:
                msg = cbor.load(f_in)
            except IOError as e:
                if e.errno == 29:
                    break
                raise

            if not isinstance(msg, dict) or ((FIELD_CONTROL not in msg) and (FIELD_TOPIC not in msg)):
                # ignore things that we do not understand
                send_control_message(f_out, CTRL_NOT_UNDERSTOOD, "Protocol mismatch")
                send_control_message(f_out, CTRL_OVER)

            if FIELD_CONTROL in msg:
                c = msg[FIELD_CONTROL]

                if c == CTRL_CAPABILITIES:
                    his = msg[FIELD_DATA]
                    logger.info('His capabilities: %s' % his)
                    capabilities = {
                        'z2': {}
                    }
                    logger.info('My capabilities: %s' % capabilities)
                    send_control_message(f_out, CTRL_UNDERSTOOD)
                    send_control_message(f_out, CTRL_CAPABILITIES, capabilities)
                    send_control_message(f_out, CTRL_OVER)
                else:
                    msg = 'Could not deal with control message "%s".' % c
                    send_control_message(f_out, CTRL_NOT_UNDERSTOOD, msg)
                    send_control_message(f_out, CTRL_OVER)

            elif FIELD_TOPIC in msg:
                topic = msg[FIELD_TOPIC]
                data = msg.get(FIELD_DATA, None)

                fn = 'on_received_%s' % topic
                if not hasattr(agent, fn):
                    msg = 'Could not deal with topic %s' % topic
                    send_control_message(f_out, CTRL_NOT_UNDERSTOOD, msg)
                    send_control_message(f_out, CTRL_OVER)
                else:
                    send_control_message(f_out, CTRL_UNDERSTOOD)

                    context = ConcreteContext(f_out)
                    f = getattr(agent, fn)
                    try:
                        f(context=context, data=data)
                    except BaseException:
                        s = traceback.format_exc()
                        logger.error(s)
                        try:
                            s = s.decode('utf-8')
                        except:
                            pass
                        send_control_message(f_out, CTRL_ABORTED, s)
                        raise
                    finally:
                        send_control_message(f_out, CTRL_OVER)


            else:
                send_control_message(f_out, CTRL_NOT_UNDERSTOOD, "I expect a topic message")
                send_control_message(f_out, CTRL_OVER)

        logger.info('Graceful exit.')
    except BaseException:
        f_out.flush()
        logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        f_out.flush()


def send_control_message(f_out, c, msg=None):
    m = {}
    m[FIELD_COMPAT] = [PROTOCOL]
    m[FIELD_CONTROL] = unicode(c)
    m[FIELD_DATA] = msg
    cbor.dump(m, f_out)
    # logger.info('Sending control %s' % c)
    f_out.flush()


def send_topic_message(f_out, topic, data):
    m = {}
    m[FIELD_COMPAT] = [PROTOCOL]
    m[FIELD_TOPIC] = unicode(topic)
    m[FIELD_DATA] = data
    cbor.dump(m, f_out)
    # logger.info('Sending topic %s' % topic)
    f_out.flush()


class ConcreteContext(Context):
    def __init__(self, f_out):
        self.f_out = f_out

    def info(self, s):
        logger.info(s)

    def error(self, s):
        logger.error(s)

    def debug(self, s):
        logger.debug(s)

    def warning(self, s):
        logger.warning(s)

    def write(self, topic, data=None):
        send_topic_message(self.f_out, topic, data)
