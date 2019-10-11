import os
import sys
import time
import json
from blowpipe import utils
from blowpipe import model_db
from blowpipe import constants
from blowpipe.scheduler import Scheduler
from blowpipe.logger import Logger, FileWriterObserver
from blowpipe import server_grpc
from datetime import datetime
from blowpipe import App
from blowpipe.config import BlowpipeConfig


class BlowpipeServerConfig(BlowpipeConfig):
    def __init__(self, filename=None):
        super(BlowpipeServerConfig, self).__init__(filename)
        self.is_repository = False


class BlowpipeServer:
    def __init__(self, config, db=None, scheduler=None, grpc_server=None):
        self.config = config
        App.Config = self.config
        self._setup_dirs()
        self._started = datetime.today()
        self.threadpool = utils.ThreadPool()

        syslog_filename = os.path.abspath(config.get_syslog_filename())
        Logger.add_global_observer(FileWriterObserver(syslog_filename))
        self.logger = Logger("BlowpipeServer")

        cur_dir = os.getcwd()
        root_dir = config.get_root_dir()
        os.chdir(root_dir)
        if db is None:
            self.db = model_db.DB(
                self.config, sqlite_filename="sqlite:///" + root_dir + "/blowpipe.db"
            )

        App.DB = self.db
        db_filename = config.get_root_dir() + "/blowpipe.db"
        db_filename = db_filename.replace("//", "/")
        if not os.path.isfile(db_filename):
            Logger.console(
                "BlowpipeServer(), '" + db_filename + "' does not exist, creating."
            )
            self.db.reset()
            Logger.console("BlowpipeServer(), '" + db_filename + "' created.")
        else:
            Logger.console("BlowpipeServer(), using '" + db_filename + "'.")
            self.db.connect()

        os.chdir(cur_dir)

        if scheduler is None:
            self.scheduler = Scheduler(self)
        else:
            self.scheduler = scheduler

        if grpc_server is None:
            self.grpc_server = server_grpc.GRPCServer(self)
        else:
            self.grpc_server = grpc_server

        if self.config.is_web_server_enabled():
            from blowpipe import server_flask

            self.web_server = server_flask.WebServer(self)

        App.Server = self

    def _setup_dirs(self):
        config = self.config
        root_dir = config.get_root_dir()
        if not os.path.isdir(root_dir):
            os.makedirs(config.get_root_dir())

        if not os.path.isfile(config.get_filename()):
            config.save()

        log_dir = config.get_log_dir()
        syslog_filename = config.get_syslog_filename()
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
            time.sleep(0.5)

        # if not os.path.isfile(syslog_filename):
        #     f = open(syslog_filename, "w")
        #     f.write("")
        #     f.close()

    def get_started(self):
        return self._started

    def get_db(self):
        return self.db

    def get_threadpool(self):
        return self.threadpool

    def get_scheduler(self):
        return self.scheduler

    def get_grpc_server(self):
        return self.grpc_server

    def start(self, blocking=True):
        """
        commences the scheduler, grpc, webserver threads
        blocking indicates if this is a blocking call
        :param blocking:
        :return:
        """

        if not utils.is_port_available("0.0.0.0", self.config.get_grpc_port()):
            raise utils.BlowpipeError("Port is already in use.")
        elif utils.is_server_running(self.config):
            raise utils.BlowpipeError("Server is already running.")

        if not self.config.is_repository:
            self.threadpool.add(self.scheduler)
        else:
            self.logger.console("Running as repository only; will not trigger any jobs.")

        self.threadpool.add(self.grpc_server)

        if self.config.is_web_server_enabled():
            self.threadpool.add(self.web_server)

        logger = self.logger
        logger.console(
            ">>>>> v"
            + constants.SERVER_VERSION
            + ", serving "
            + self.config.get_grpc_server_ip()
            + ":"
            + str(self.config.get_grpc_port())
        )
        if blocking:
            logger.debug(".start(blocking=True)")
            while self.threadpool.is_running():
                try:
                    time.sleep(0.1)
                except KeyboardInterrupt as e:
                    logger.debug(".start() interrupt() (CTRL-C) quitting threads.")
                    self.threadpool.quit()
        else:
            logger.debug(".start(); not blocking.")

    def stop(self):
        """
        stops all threads in the threadpool (scheduler, GRPC, WebServer)
        :return:
        """
        self.threadpool.quit()
        while self.threadpool.is_running():
            time.sleep(0.1)

    def tick(self):
        """
        instructs the scheduler to perform one
        synchronisation 'tick', returning a scheduler.Report
        :return:
        """
        self.logger.debug(".tick()")
        report = self.scheduler.check()
        return report

    def manual_trigger(self, workflow_definition, session):
        """
        creates and returns WorkflowInstance, marks the state as constants.STATE_TRIGGER_MANUAL
        the scheduler will pick it up on the next tick()
        :param workflow_definition:
        :param session:
        :return:
        """
        job = self.db.build_instance(workflow_definition, session)
        job.is_active = True
        job.state = constants.STATE_TRIGGER_MANUAL
        job.save(session)
        return job
