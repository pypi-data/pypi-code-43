#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
***
Module:
***

https://mattgathu.github.io/multiprocessing-logging-in-python/

 Copyright (C) Smart Arcs Ltd, registered in the United Kingdom.
 This file is owned exclusively by Smart Arcs LTd.
 Unauthorized copying of this file, via any medium is strictly prohibited
 Proprietary and confidential
 Written by Dan Cvrcek <support@smartarchitects.co.uk>, Feb 2019
"""
__author__ = "Dan Cvrcek"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'

import sys
import logging
import traceback
import threading
import multiprocessing
# noinspection PyCompatibility
from queue import Empty  # future is required by setup for py3
# noinspection PyPep8Naming
from logging import FileHandler as FH


# ============================================================================
# Define Log Handler
# ============================================================================
# noinspection PyMissingOrEmptyDocstring
class QueueHandler(logging.Handler):
    """multiprocessing log handler

    This handler makes it possible for several processes
    to log to the same file by using a queue.

    """
    def __init__(self, fname=None):
        logging.Handler.__init__(self)

        if fname:
            self._handler = FH(fname)
        else:
            self._handler = logging.StreamHandler(sys.stderr)

        self.queue = multiprocessing.Queue(-1)

        self.stop = multiprocessing.Event()

        thrd = threading.Thread(target=self.receive, args=(self.stop,), name="log listener")
        thrd.daemon = True
        thrd.start()

    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)
        self._handler.setFormatter(fmt)

    def setLevel(self, level):
        self._handler.setLevel(level)

    def receive(self, stop_event):
        """

        :param stop_event
        :type stop_event: multiprocessing.Event
        :rtype: object
        """
        while not stop_event.is_set():  # type: multiprocessing.Event
            try:
                record = self.queue.get(timeout=2)
                if record is not None:
                    self._handler.emit(record)
            except Empty:
                pass  # empty queue
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                break
            except BaseException as ex:
                traceback.print_exc(file=sys.stderr)
                sys.stderr.write("Exception in queue_handler %s" % str(ex))

    def send(self, s):
        self.queue.put_nowait(s)

    def _format_record(self, record):
        if record.args:
            record.msg = record.msg % record.args
            record.args = None
        if record.exc_info:
            # noinspection PyUnusedLocal
            dummy = self.format(record)
            record.exc_info = None

        return record

    def emit(self, record):
        """

        :param self:
        :param record:
        """
        # noinspection PyBroadException
        try:
            s = self._format_record(record)
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException:
            self.handleError(record)

    def close(self):
        self._handler.close()
        self.stop.set()
        logging.Handler.close(self)
