from __future__ import unicode_literals

import os
import socket
import time
import traceback
from collections import namedtuple

import cbor2 as cbor


from . import logger
from .constants import *
from .reading import read_next_cbor
from .utils import indent

# Python 2 compatibility.
try:
    TimeoutError
except NameError:
    import socket
    TimeoutError = socket.timeout

__all__ = ['ComponentInterface']


class ExternalProtocolViolation(Exception):
    pass


class ExternalNodeDidNotUnderstand(Exception):
    pass


class RemoteNodeAborted(Exception):
    pass


TimeoutError = socket.timeout
class Malformed(Exception):
    pass


MsgReceived = namedtuple('MsgReceived', 'topic data')


class ComponentInterface(object):

    def __init__(self, fnin, fnout, nickname, timeout=None):
        self.nickname = nickname
        try:
            os.mkfifo(fnin)
        except BaseException as e:
            msg = 'Cannot create fifo {}'.format(fnin)
            msg += '\n\n%s' % traceback.format_exc()
            raise Exception(msg)
        self.fpin = open(fnin, 'wb', buffering=0)
        wait_for_creation(fnout)
        self.fnout = fnout
        f = open(fnout, 'rb', buffering=0)
        # noinspection PyTypeChecker
        self.fpout = f  # BufferedReader(f, buffer_size=1)
        self.nreceived = 0
        self.node_protocol = None
        self.data_protocol = None
        self.timeout = timeout

    def close(self):
        self.fpin.close()
        self.fpout.close()

    def write_topic_and_expect(self, topic, data=None,
                               timeout=None,
                               timing=None,
                               expect=None):
        timeout = timeout or self.timeout
        self._write_topic(topic, data=data, timing=timing)
        ob = self.read_one(expect_topic=expect, timeout=timeout)
        return ob

    def write_topic_and_expect_zero(self, topic, data=None,
                                    timeout=None,
                                    timing=None):
        timeout = timeout or self.timeout
        self._write_topic(topic, data=data, timing=timing)
        msgs = read_reply(self.fpout, timeout=timeout,
                          nickname=self.nickname)
        if msgs:
            msg = 'Expecting zero, got %s' % msgs
            raise ExternalProtocolViolation(msg)

    def _write_topic(self, topic, data=None, timing=None):

        msg = {FIELD_COMPAT: [PROTOCOL],
               FIELD_TOPIC: topic,
               FIELD_DATA: data,
               FIELD_TIMING: timing}
        j = self._serialize(msg)
        self._write(j)

        # logger.info('Written to topic "{topic}" >> {name}.'.format(topic=topic, name=self.nickname))

    def _write(self, j):

        try:
            self.fpin.write(j)
            self.fpin.flush()
        except BrokenPipeError as e:
            msg = ('While attempting to write to node "{nickname}", '
                   'I reckon that the pipe is closed and the node exited.').format(nickname=self.nickname)
            try:
                received = self.read_one(expect_topic=TOPIC_ABORTED)
                if received.topic == TOPIC_ABORTED:
                    msg += '\n\nThis is the aborted message:'
                    msg += '\n\n' + received.data
            except BaseException as e2:
                msg += '\n\nI could not read any aborted message: {e2}'.format(e2=e2)
            raise RemoteNodeAborted(msg)

    def _serialize(self, msg):
        j = cbor.dumps(msg)
        return j

    def read_one(self, expect_topic=None, timeout=None):
        timeout = timeout or self.timeout
        try:
            if expect_topic:
                waiting_for = 'Expecting topic "{expect_topic}" << {nickname}.'.format(expect_topic=expect_topic,
                                                                                       nickname=self.nickname)
            else:
                waiting_for = None

            msgs = read_reply(self.fpout, timeout=timeout, waiting_for=waiting_for,
                              nickname=self.nickname)

            if len(msgs) == 0:
                msg = 'Expected one message from node "{}". Got zero.'.format(self.nickname)
                if expect_topic:
                    msg += '\nExpecting topic "{}".'.format(expect_topic)
                raise ExternalProtocolViolation(msg)
            if len(msgs) > 1:
                msg = 'Expected only one message. Got {}.'.format(len(msgs))
                raise ExternalProtocolViolation(msg)
            msg = msgs[0]

            if FIELD_TOPIC not in msg:
                m = 'Invalid message does not contain the field "{}".'.format(FIELD_TOPIC)
                m += '\n {}'.format(msg)
                raise ExternalProtocolViolation(m)
            topic = msg[FIELD_TOPIC]

            if expect_topic:
                if topic != expect_topic:
                    msg = 'I expected topic "{expect_topic}" but received "{topic}".'.format(expect_topic=expect_topic,
                                                                                             topic=topic)
                    raise ExternalProtocolViolation(msg)

            if self.nreceived == 0:
                msg1 = 'Received first message of topic %s' % topic
                logger.info(msg1)
            self.nreceived += 1
            return MsgReceived(topic, msg[FIELD_DATA])

        except StopIteration as e:
            msg = 'EOF detected on %s after %d messages.' % (self.fnout, self.nreceived)
            if expect_topic:
                msg += ' Expected topic "{}".'.format(expect_topic)
            raise StopIteration(msg)
        except TimeoutError as e:
            msg = 'Timeout declared after waiting %s sec on %s after having received %d messages.' % (timeout,
                                                                                                    self.fnout,
                                                                                     self.nreceived)
            if expect_topic:
                msg += ' Expected topic "{}".'.format(expect_topic)
            raise TimeoutError(msg)


def wait_for_creation(fn):
    while not os.path.exists(fn):
        msg = 'waiting for creation of %s' % fn
        logger.info(msg)
        time.sleep(1)


def read_reply(fpout, nickname, timeout=None, waiting_for=None):
    """ Reads a control message. Returns if it is CTRL_UNDERSTOOD.
     Raises:
         TimeoutError
         RemoteNodeAborted
         ExternalNodeDidNotUnderstand
         ExternalProtocolViolation otherwise. """
    try:
        wm = read_next_cbor(fpout, timeout=timeout, waiting_for=waiting_for)

    except StopIteration:
        msg = 'Remote node closed communication (%s)' % waiting_for
        raise RemoteNodeAborted(msg)

    cm = interpret_control_message(wm)
    if cm.code == CTRL_UNDERSTOOD:
        others = read_until_over(fpout, timeout=timeout, nickname=nickname)
        return others
    elif cm.code == CTRL_ABORTED:
        msg = 'The remote node "{}" aborted with the following error:'.format(nickname)
        msg += '\n\n' + indent(cm.msg, "|", "error in {} |".format(nickname))
        # others = self.read_until_over()
        raise RemoteNodeAborted(msg)
    elif cm.code == CTRL_NOT_UNDERSTOOD:
        _others = read_until_over(fpout, timeout=timeout, nickname=nickname)
        msg = 'The remote node "{nickname}" reports that it did not understand the message:'.format(nickname=nickname)
        msg += '\n\n' + indent(cm.msg, "|", "reported by {} |".format(nickname))
        raise ExternalNodeDidNotUnderstand(msg)
    else:
        msg = 'Remote node raised unknown code %s: %s' % (cm, cm.code)
        raise ExternalProtocolViolation(msg)


ControlMessage = namedtuple('ControlMessage', 'code msg')


def interpret_control_message(m):
    if not isinstance(m, dict):
        msg = 'Expected dictionary, not {}.'.format(type(m))
        raise Malformed(msg)
    if not FIELD_CONTROL in m:
        msg = 'Expected field {}, obtained {}'.format(FIELD_CONTROL, list(m))
        raise Malformed(msg)
    code = m[FIELD_CONTROL]
    msg = m.get(FIELD_DATA, None)
    return ControlMessage(code, msg)


def read_until_over(fpout, timeout, nickname):
    """ Raises RemoteNodeAborted, TimeoutError """
    res = []
    waiting_for = 'Reading reply of {}.'.format(nickname)
    while True:
        try:
            wm = read_next_cbor(fpout, timeout=timeout, waiting_for=waiting_for)
            if wm.get(FIELD_CONTROL, '') == CTRL_ABORTED:
                m = 'External node "{}" aborted:'.format(nickname)
                m += '\n\n' + indent(wm.get(FIELD_DATA, None), "|",
                                    "error in {} |".format(nickname))
                raise RemoteNodeAborted(m)
            if wm.get(FIELD_CONTROL, '') == CTRL_OVER:
                # logger.info(f'Node "{nickname}" concluded output of %s messages.' % len(res))
                break
            # logger.info(f'Node "{nickname}" sent %s.' % len(wm))
        except StopIteration:
            msg = 'External node "{}" closed communication.'.format(nickname)
            raise RemoteNodeAborted(msg)
        except TimeoutError:
            msg = 'Timeout while reading output of node "{}".'.format(nickname)
            raise TimeoutError(msg)
        res.append(wm)
    return res
