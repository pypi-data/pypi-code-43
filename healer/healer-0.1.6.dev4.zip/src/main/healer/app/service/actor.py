"""
Healer service
"""

from __future__ import annotations

import logging
import os
import signal
import sys
from typing import Any

from healer.cluster.arkon import ClusterActor
from healer.config import CONFIG
from healer.device.bt.arkon import ManagerBT
from healer.device.usb.arkon import ManagerUSB
from healer.station.server.arkon import FlaskServer
from healer.station.server.arkon import FlaskSupport
from healer.support.actor.master import MasterActor
from healer.support.actor.proper import ProperRef
from healer.support.files import FilesPathLock
from healer.support.files import FilesSupport
from healer.support.typing import override

logger = logging.getLogger(__name__)


class MainActor(
        MasterActor,
    ):
    """
    """
    use_daemon_thread = False  # keep from exit

    manager_bt:ManagerBT = None
    manager_usb:ManagerUSB = None
    flask_server:FlaskServer = None

    @override
    def on_start(self):
        logger.info(f"on_start")
        super().on_start()
        self.flask_server = FlaskSupport.produce_server()
        self.worker_start(ClusterActor)
        self.flask_server.start()
        self.manager_bt = ManagerBT()
        self.manager_usb = ManagerUSB()
        self.manager_bt.observer_start()
        self.manager_usb.observer_start()

    @override
    def on_stop(self):
        logger.info(f"on_stop")
        self.manager_bt.observer_stop()
        self.manager_usb.observer_stop()
        self.flask_server.stop()
        super().on_stop()

    @override
    def on_receive(self, message:Any) -> Any:
        logger.info(f"on_receive")
        super().on_receive(message)


class MainSupport():
    """
    """

    main_actor:ProperRef = None
    storage_lock:FilesPathLock = None

    @staticmethod
    def initiate():
        logger.info(f"startup")
        MainSupport.storage_lock = MainSupport.produce_lock()
        MainSupport.main_actor = MainSupport.produce_actor()
        MainSupport.setup_system_signal()

    @staticmethod
    def terminate(*_) -> None:
        logger.info(f"shutdown")
        MainSupport.main_actor.stop()
        MainSupport.storage_lock.release()

    @staticmethod
    def produce_lock() -> FilesPathLock:
        storage_root = CONFIG['storage']['root']
        if not os.path.exists(storage_root):
            logger.error(f"missing storage root: {storage_root}")
            sys.exit(-1)
        storage_lock = FilesPathLock(storage_root)
        if not storage_lock.aquire():
            logger.error(f"failed to lock storage: {storage_root}")
            sys.exit(-1)
        if not FilesSupport.has_writable(storage_root):
            logger.error(f"storage not writable: {storage_root}")
            sys.exit(-1)
        return storage_lock

    @staticmethod
    def produce_actor() -> ProperRef:
        return MainActor.start()

    @staticmethod
    def setup_system_signal() -> None:
        "intercept regular termination signals"
        signal.signal(signal.SIGINT, MainSupport.terminate)
        signal.signal(signal.SIGTERM, MainSupport.terminate)
        signal.signal(signal.SIGHUP, MainSupport.terminate)
        signal.signal(signal.SIGUSR1, MainSupport.terminate)
        signal.signal(signal.SIGUSR2, MainSupport.terminate)
