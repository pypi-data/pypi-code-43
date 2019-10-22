import os
import signal
import subprocess
from datetime import datetime
from logging import Logger
from typing import List

from sidecar.app_instance_identifier import IIdentifier
from sidecar.health_check.health_check_executor_logger import HealthCheckExecutorLogger
from sidecar.model.objects import SidecarApplication
from sidecar.non_blocking_stream_reader import NonBlockingStreamReader
from sidecar.services.metadata.sandbox_public_address_fetcher import SandboxPublicAddressFetcher
from sidecar.services.input_value_resolver import InputValueResolver
from sidecar.utils import CallsLogger


class HealthCheckExecutor:

    def __init__(self,
                 input_resolver: InputValueResolver,
                 apps: List[SidecarApplication],
                 executor_logger: HealthCheckExecutorLogger,
                 logger: Logger,
                 sandbox_id: str,
                 sandbox_public_address_fetcher: SandboxPublicAddressFetcher):
        self._input_resolver = input_resolver
        self._apps = apps
        self._executor_logger = executor_logger
        self._logger = logger
        self._sandbox_id = sandbox_id
        self._domain_name = f'{sandbox_id}.sandbox.com'
        self._sandbox_public_address_fetcher = sandbox_public_address_fetcher

    @CallsLogger.wrap
    def start(self, identifier: IIdentifier, cmd: List[str]) -> bool:

        app = next(iter([app for app in self._apps if app.name == identifier.name]), None)  # type: SidecarApplication

        self._executor_logger.log_start(identifier=identifier, cmd=cmd, timeout=app.healthcheck_timeout)

        resolved_inputs = self.resolve_inputs(app)

        env = {**os.environ, **resolved_inputs}

        sandbox_publie_address = self._sandbox_public_address_fetcher.get_value() if self._sandbox_public_address_fetcher else ''
        env.update({
            'DOMAIN_NAME': self._domain_name,
            'SANDBOX_ID': self._sandbox_id,
            'PUBLIC_ADDRESS': sandbox_publie_address,
            'COLONY_DOMAIN_NAME': self._domain_name,
            'COLONY_SANDBOX_ID': self._sandbox_id,
            'COLONY_PUBLIC_ADDRESS': sandbox_publie_address})

        start = datetime.now()
        timed_out = False
        read_interval = 0.5
        
        """
        run healthcheck command in subprocess and redirect its outputs to subprocess' stdout
        read stdout line by line until subprocess ended or until timeout and send it to cloud logger
        if timeout occurred kill healthcheck subprocess
        """
        with subprocess.Popen(cmd,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              shell=True,
                              preexec_fn=os.setsid,
                              universal_newlines=True,
                              env=env) as p:
            try:
                stdout_stream_reader = NonBlockingStreamReader(stream=p.stdout, interval=read_interval)
                stderr_stream_reader = NonBlockingStreamReader(stream=p.stderr, interval=read_interval)
                self._logger.info('running command {0}'.format(cmd))

                while True:
                    line = stdout_stream_reader.read_line(read_interval)
                    if line:
                        self._executor_logger.log_line(line, identifier)

                    line = stderr_stream_reader.read_line(read_interval)
                    if line:
                        self._executor_logger.log_line(line, identifier, True)

                    elapsed = datetime.now() - start

                    if elapsed.total_seconds() > app.healthcheck_timeout:
                        stdout_stream_reader.stop()
                        stderr_stream_reader.stop()
                        raise subprocess.TimeoutExpired(cmd=cmd, timeout=app.healthcheck_timeout)

                    # if process has terminated - drain the streams and exit the loop
                    if p.poll() is not None:
                        stdout_stream_reader.stop()
                        stderr_stream_reader.stop()

                        for line in stdout_stream_reader.read_lines():
                            self._executor_logger.log_line(line, identifier)

                        for line in stderr_stream_reader.read_lines():
                            self._executor_logger.log_line(line, identifier, True)

                        break
            except subprocess.TimeoutExpired as ex:
                self._executor_logger.log_timeout(timeout=ex.timeout, identifier=identifier)
                self._kill_process(process=p)
                timed_out = True
            finally:
                if timed_out:
                    return False
                process_exit_code = p.returncode
                if process_exit_code == 0:
                    self._executor_logger.log_success(identifier=identifier)
                    return True
                else:
                    self._executor_logger.log_error(identifier=identifier, exit_code=process_exit_code)
                    return False

    def resolve_inputs(self, app):
        resolved_inputs = {}
        if app.env:
            for k, v in app.env.items():
                if self._input_resolver.can_resolve(v):
                    resolved_inputs[k] = self._input_resolver.resolve(v)
                else:
                    resolved_inputs[k] = v
        return resolved_inputs

    def _kill_process(self, process):
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except ProcessLookupError as ex:
            self._logger.exception('Could not kill process, pid {} due to {}'.format(
                process.pid,
                str(ex)))
