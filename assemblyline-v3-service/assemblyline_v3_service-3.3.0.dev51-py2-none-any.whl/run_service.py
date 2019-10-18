#!/usr/bin/env python

import json
import logging
import os
import select
import signal
import sys
import tempfile
import threading
import time

import yaml

from assemblyline_v3_service.common import log as al_log
from assemblyline_v3_service.common.dict_utils import recursive_update
from assemblyline_v3_service.common.importing import load_module_by_path
from assemblyline_v3_service.common.mock_modules import modules1, modules2
from assemblyline_v3_service.common.task import Task

SERVICE_PATH = os.environ['SERVICE_PATH']
SERVICE_NAME = SERVICE_PATH.split(".")[-1].lower()
SHUTDOWN_SECONDS_LIMIT = 10
TASK_FIFO_PATH = "/tmp/task.fifo"
DONE_FIFO_PATH = "/tmp/done.fifo"

SUCCESS = "RESULT_FOUND"
ERROR = "ERROR_FOUND"

al_log.init_logging()
LOGGER = logging.getLogger('assemblyline.svc.{}'.format(SERVICE_NAME))

modules1()
modules2()


class RunService(threading.Thread):
    """
    Inheriting from thread so that the main work is done off the main thread.
    This lets the main thread handle interrupts properly, even when the workload
    makes a blocking call that would normally stop this.
    """

    def __init__(self, shutdown_timeout=SHUTDOWN_SECONDS_LIMIT):
        super(RunService, self).__init__()

        self.running = None
        self._exception = None
        self._traceback = None
        self._shutdown_timeout = shutdown_timeout

        self.classification_yml = '/etc/assemblyline/classification.yml'
        self.service_manifest_yml = os.path.join(tempfile.gettempdir(), 'service_manifest.yml')

        self.shutdown_timeout = shutdown_timeout
        self.status = None

        self.service_name = None
        self.service_version = None
        self.service_tool_version = None
        self.service_category = None
        self.service_stage = None
        self.file_required = None
        self.task_fifo = None
        self.done_fifo = None

    def __enter__(self):
        LOGGER.info("Initialized")
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        self.close()
        if _exc_type is not None:
            LOGGER.exception("Terminated because of an {} exception".format(_exc_type))
        else:
            LOGGER.info('Terminated')

    def __stop(self):
        """Hard stop"""
        time.sleep(self._shutdown_timeout)
        LOGGER.error(str(threading.enumerate()))
        LOGGER.error("Server has shutdown hard after waiting {} seconds to stop".format(self._shutdown_timeout))
        exit(1)

    def close(self):
        pass

    def interrupt_handler(self, _signum, _stack_frame):
        LOGGER.info("Instance caught signal. Coming down...")
        self.stop()

    def raising_join(self):
        self.join()
        if self._traceback and self._exception:
            raise self._exception.with_traceback(self._traceback)

    def run(self):
        try:
            self.try_run()
        except Exception:
            _, self._exception, self._traceback = sys.exc_info()
            LOGGER.exception("Exiting:")

    def serve_forever(self):
        self.start()
        self.join()

    def start(self):
        """Start the server workload."""
        self.running = True
        super(RunService, self).start()
        LOGGER.info("Started")
        signal.signal(signal.SIGINT, self.interrupt_handler)
        signal.signal(signal.SIGTERM, self.interrupt_handler)

    def stop(self):
        """Ask nicely for the server to stop.

        After a timeout, a hard stop will be triggered.
        """
        # The running loops should stop within a few seconds of this flag being set.
        self.running = False

        # If it doesn't stop within a few seconds, this other thread should kill the entire process
        stop_thread = threading.Thread(target=self.__stop)
        stop_thread.daemon = True
        stop_thread.start()

    def try_run(self):
        try:
            self.svc_class = load_module_by_path(SERVICE_PATH)
        except:
            LOGGER.error("Could not find service in path.")
            raise

        cfg = self.get_service_config()

        # Start task receiving fifo
        LOGGER.info('Waiting for receive task named pipe to be ready...')
        if not os.path.exists(TASK_FIFO_PATH):
            os.mkfifo(TASK_FIFO_PATH)
        self.task_fifo = open(TASK_FIFO_PATH, "r")

        # Start task completing fifo
        LOGGER.info('Waiting for complete task named pipe to be ready...')
        if not os.path.exists(DONE_FIFO_PATH):
            os.mkfifo(DONE_FIFO_PATH)
        self.done_fifo = open(DONE_FIFO_PATH, "w")

        service = self.svc_class(cfg)
        service.start_service()

        try:
            while self.running:
                try:
                    read_ready, _, _ = select.select([self.task_fifo], [], [], 1)
                    if not read_ready:
                        continue
                except ValueError:
                    LOGGER.info('Task fifo is closed. Cleaning up...')
                    return

                task_json_path = self.task_fifo.readline().strip()
                if not task_json_path:
                    LOGGER.info('Received an empty message for Task fifo. Cleaning up...')
                    return

                LOGGER.info("Task found in: {}".format(task_json_path))
                with open(task_json_path, 'r') as f:
                    task = Task(json.load(f))
                service.handle_task(task)

                # Notify task handler that processing is done
                result_json = os.path.join(tempfile.gettempdir(), "{}_{}_result.json".format(task.sid, task.sha256))
                error_json = os.path.join(tempfile.gettempdir(), "{}_{}_error.json".format(task.sid, task.sha256))
                if os.path.exists(result_json):
                    msg = "{}\n".format(json.dumps([result_json, SUCCESS]))
                elif os.path.exists(error_json):
                    msg = "{}\n".format(json.dumps([error_json, ERROR]))
                else:
                    msg = "{}\n".format(json.dumps([None, ERROR]))

                self.done_fifo.write(msg)
                self.done_fifo.flush()

        except Exception as e:
            LOGGER.error(str(e))
        finally:
            LOGGER.info("Closing named pipes...")
            if self.done_fifo is not None:
                self.done_fifo.close()
            if self.task_fifo is not None:
                self.task_fifo.close()

            service.stop_service()

    def get_service_config(self, yml_config=None):
        if yml_config is None:
            yml_config = os.path.join(tempfile.gettempdir(), 'service_manifest.yml')

        service_config = {}
        default_file = os.path.join(os.path.dirname(__file__), 'common', 'default_service_manifest.yml')
        if os.path.exists(default_file):
            with open(default_file, 'r') as default_fh:
                default_service_config = yaml.safe_load(default_fh.read())
                if default_service_config:
                    service_config.update(default_service_config)

        # Load modifiers from the service
        service = self.svc_class(cfg={})
        service_config = recursive_update(service_config, service.get_default_config())

        service_config['version'] = service.get_service_version()
        service_config['tool_version'] = service.get_tool_version()
        service_config['docker_config']['image'] = 'cccs/alsvc_{}:latest'.format(service_config['name'].lower())
        service_config['docker_config']['cpu_cores'] = self.svc_class.SERVICE_CPU_CORES
        service_config['docker_config']['ram_mb'] = self.svc_class.SERVICE_RAM_MB

        with open(yml_config, 'w') as yml_fh:
            yaml.safe_dump(service_config, yml_fh)

        return service_config['config']


if __name__ == '__main__':
    RunService().serve_forever()
