# -*- coding: future_fstrings -*-
from abc import ABCMeta, abstractmethod
import sys
import os
import six
import datetime
from common.logger import get_logger
from common.utils import get_current_timestamp, compatibleabstractproperty
from omnistorage.factory import ProviderFactory
from common.config import Config


@six.add_metaclass(ABCMeta)
class BaseOutputHandler(object):

    def __init__(self, config, *args, **kwargs):
        self.log = get_logger(__name__, force_create=True, **config['Logging'])
        self.setUp(config, *args, **kwargs)

    @abstractmethod
    def setUp(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def send(self, data):
        raise NotImplementedError()


@six.add_metaclass(ABCMeta)
class BaseCollector(object):

    def __init__(self, PROJECT_DIR):
        cfgpath = sys.argv[1] if len(sys.argv) > 1 else ''
        self.config = Config().get_config(self.CONFIG_FILENAME, PROJECT_DIR, cfgpath)
        self.log = get_logger(__name__, force_create=True, **self.config['Logging'])
        self.collection_config = self.config['Collection']
        op_cli = ProviderFactory.get_provider(self.collection_config['ENVIRONMENT'])
        self.kvstore = op_cli.get_storage("keyvalue", logger=self.log, name=self.collection_config['DBNAME'], db_dir=self.collection_config.get("DB_DIR"))


    @compatibleabstractproperty
    def CONFIG_FILENAME(self):
        raise NotImplementedError()


    @compatibleabstractproperty
    def SINGLE_PROCESS_LOCK_KEY(self):
        raise NotImplementedError()

    @abstractmethod
    def build_task_params(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError()

    def is_process_running(self, cmd_names):
        if not isinstance(cmd_names, list):
            cmd_names = [cmd_names]

        is_process_running = False
        if self.collection_config['ENVIRONMENT'] == "onprem":
            import psutil
            current_pid = os.getpid()
            for procobj in psutil.process_iter(attrs=['cmdline', 'pid']):
                cmds = procobj.info['cmdline']
                process_id = procobj.info['pid']
                if cmds:
                    cmdline = " ".join(cmds)
                    if any([cmd_name in cmdline and process_id != current_pid for cmd_name in cmd_names]):
                        self.log.info("running cmd line: %s process_id: %s current_pid: %s" % (
                                cmdline, process_id, current_pid))
                        is_process_running = True
                        break
        return is_process_running

@six.add_metaclass(ABCMeta)
class BaseAPI(object):
    # Todo pagination/auth/

    def __init__(self, kvstore, config):
        self.kvstore = kvstore
        self.config = config
        self.start_time = datetime.datetime.utcnow()
        self.sumo_config = config['SumoLogic']
        self.collection_config = self.config['Collection']
        self.STOP_TIME_OFFSET_SECONDS = self.collection_config['TIMEOUT']
        self.DEFAULT_START_TIME_EPOCH = get_current_timestamp() - self.collection_config['BACKFILL_DAYS']*24*60*60
        self.log = get_logger(__name__, force_create=True, **self.config['Logging'])

    def get_function_timeout(self):
        timeout_config = {
            "onprem": float("Inf"),
            "aws": 15*60,
            "gcp": 5*60,
            "azure": 5*60
        }
        return timeout_config[self.collection_config['ENVIRONMENT']]

    def is_time_remaining(self):
        now = datetime.datetime.utcnow()
        time_passed = (now - self.start_time).total_seconds()
        self.log.debug("checking time_passed: %s" % time_passed)
        has_time = time_passed + self.STOP_TIME_OFFSET_SECONDS < self.get_function_timeout()
        if not has_time:
            self.log.info("Shutting down not enough time")
        return has_time

    def __str__(self):
        return self.get_key()

    @abstractmethod
    def get_key(self):
        raise NotImplementedError()

    @abstractmethod
    def save_state(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def get_state(self):
        raise NotImplementedError()

    @abstractmethod
    def build_fetch_params(self):
        raise NotImplementedError()

    @abstractmethod
    def build_send_params(self):
        raise NotImplementedError()

    @abstractmethod
    def transform_data(self, content):
        raise NotImplementedError()

    @abstractmethod
    def fetch(self):
        raise NotImplementedError()
