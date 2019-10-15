#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
***
Module: beacon_thread - Implementation of a process checking availability of the upstream server
***
"""

# Copyright (C) Smart Arcs Ltd registered in the United Kingdom.
# Unauthorized copying of this file, via any medium is strictly prohibited
#
# This file is provided under a license as specified in the "LICENSE" file, which is part
# of this software package.
#
# Written by Smart Arcs <support@smartarchitects.co.uk>, August 2018
import logging
import threading
from traceback import print_exc
import datetime
from multiprocessing import Event

from foxyproxy.csp import WorkerMap

__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'

logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# logger.addHandler(ch)


# noinspection PyUnusedLocal
class BeaconThread(threading.Thread):
    """
    Class starts a thread, which regularly connects to a restful upstream and re-builds a dictionary of certificates
    when the upstream restarts
    """
    WORKERS = WorkerMap()

    def __init__(self, signer,  interval=10):
        """
        :param signer: an instance of the signer - crypto provider, which also wraps the upstream server configuration
        :type signer: BaseCryptoService
        :param interval: how often we check whether the upstream server needs refresh
        :type interval: int
        """
        threading.Thread.__init__(self)
        self.server = signer  # Type[BaseUpstream]
        self.interval = interval
        self.stop_event = Event()  # type: Event
        self.upstream = self.server.getupstreamconnection()
        pass

    def run(self):
        """
        The main thread processing method.
        """
        throwaway = datetime.datetime.strptime('20110101', '%Y%m%d')
        last_time = 0
        while not self.stop_event.is_set():
            # noinspection PyBroadException
            try:
                self.server.init(self.upstream)

                BeaconThread.WORKERS.instance_lock.acquire()
                # noinspection PyBroadException
                try:
                    # update the map and worker dictionary
                    existing_map = list(BeaconThread.WORKERS.map.keys())
                    for each_reader in self.server.storage.certificates:
                        if each_reader in existing_map:
                            existing_map.remove(each_reader)  # mark those that still exist

                        if each_reader in BeaconThread.WORKERS.map:
                            pass
                        else:
                            if each_reader in BeaconThread.WORKERS.map_all:
                                BeaconThread.WORKERS.map[each_reader] = BeaconThread.WORKERS.map_all[each_reader]
                            else:
                                if BeaconThread.WORKERS.last_mapped >= BeaconThread.WORKERS.CAPACITY:
                                    logging.error("We try to add a reader but no space. Capacity: %d"
                                                  % BeaconThread.WORKERS.CAPACITY)
                                else:
                                    BeaconThread.WORKERS.last_mapped += 1
                                    BeaconThread.WORKERS.map_all[each_reader] = BeaconThread.WORKERS.last_mapped
                                    BeaconThread.WORKERS.map[each_reader] = BeaconThread.WORKERS.last_mapped

                    # remove mapping to cards that were removed
                    for each_reader in existing_map:
                        if each_reader in BeaconThread.WORKERS.map:
                            del BeaconThread.WORKERS.map[each_reader]
                        else:
                            logging.error("Inconsistency im WORKERS.map - trying to delete reader that doesn't exist %s"
                                          % each_reader)
                except Exception:
                    pass
                finally:
                    BeaconThread.WORKERS.instance_lock.release()

                self.stop_event.wait(timeout=self.interval)  # every this many seconds, we will check up-time
                pass  # end of the infinite cycle loop
            except Exception as ex:
                # we ignore exceptions, keep running
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                logging.error(template.format(type(ex).__name__, ex.args))
                logging.debug("beacon thread %s" % print_exc())

                pass
        logging.error("Beacon thread is terminating")
        pass

    def stopnow(self):
        """
        Just stop
        """
        self.stop_event.set()
