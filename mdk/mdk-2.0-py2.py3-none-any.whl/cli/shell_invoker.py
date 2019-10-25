"""class: ShellInvoker"""
from pathlib import Path
import subprocess
from typing import List

from ..errors import ConfigError
from ..filesystem.compose_writer import ComposeWriter
from ..filesystem.config import Config
from ..filesystem.f_utils import read_compose_yaml


class ShellInvoker():
    """handles direct interaction with the docker and docker-compose cli's"""

    def __init__(self):
        self.config = Config()


    @staticmethod
    def bash_result(args, working_dir=None):
        """$ docker [args]"""
        return subprocess.check_output(
            args,
            cwd=working_dir,
            stderr=subprocess.STDOUT,
            shell=True,
        )


    def bash_result_cwd(self, args):
        """$ docker [args], from directory of current service"""
        return ShellInvoker.bash_result(
            args,
            working_dir=self.config.working_dir,
        )


    @staticmethod
    def docker_compose(
            args,
            detach=False,
            override_files: List[str] = None,
            working_dir=None):
        """$ docker-compose [args]"""
        command_builder = ["docker-compose"]
        if override_files is not None and len(override_files) > 0:
            command_builder.extend(["-f", "docker-compose.yaml"])
            for override_filename in override_files:
                command_builder.extend(["-f", override_filename])

        command_builder.extend(args)

        if not detach:
            return subprocess.call(
                command_builder,
                cwd=working_dir,
            )

        proc = subprocess.Popen(
            command_builder,
            cwd=working_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        return proc


    def docker_compose_cwd(self, args, detach=False):
        """$ docker-compose [args], from directory of current service"""
        override_files = None
        if self.config.dev_mode is True:
            dev_compose_path = self.config.working_dir/(
                "docker-compose.{}.yaml".format(self.config.dev_compose_extension)
            )
            if not dev_compose_path.exists():
                ComposeWriter.write_dev_config()
            override_files = ["docker-compose.{}.yaml".format(self.config.dev_compose_extension)]

        return ShellInvoker.docker_compose(
            args,
            detach=detach,
            override_files=override_files,
            working_dir=self.config.working_dir,
        )


    @staticmethod
    def docker(args, working_dir=None):
        """$ docker [args]"""
        return subprocess.call(
            ["docker"] + args,
            cwd=working_dir,
        )


    def docker_cwd(self, args):
        """$ docker [args], from directory of current service"""
        return ShellInvoker.docker(
            args,
            working_dir=self.config.working_dir,
        )


    def has_active_service(self) -> bool:
        """check if the user has an active service"""
        return self.config.service is not None and self.config.working_dir is not None


    def set_service(self, service):
        """set the active docker-compose service"""
        local_compose = read_compose_yaml()
        if local_compose is None:
            raise ConfigError("docker-compose.yaml not found in current directory.")
        if not "services" in local_compose:
            raise ConfigError("no 'services' section found in docker-compose.yaml")
        if not service in local_compose["services"]:
            raise ConfigError("no service \"{}\" in docker-compose.yaml".format(service))

        self.config.service = service
        self.config.working_dir = Path.cwd()
