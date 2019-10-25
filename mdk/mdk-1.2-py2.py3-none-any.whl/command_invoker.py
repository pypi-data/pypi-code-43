"""class: CommandInvoker"""
import os
from pathlib import Path
import shelve
import subprocess

from .errors import ConfigError
from .file_utils import local_compose_yaml

class CommandInvoker():
    """handles direct interaction with the docker and docker-compose cli's"""
    data_store_dir = "/tmp/"
    data_store_suffix = ".mdk"

    def __init__(self):
        self.data_store_file = "{}{}{}".format(
            CommandInvoker.data_store_dir,
            os.geteuid(),
            CommandInvoker.data_store_suffix,
        )
        self.service = self.from_store("service")
        self.working_dir = self.from_store("working_dir")


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
        return CommandInvoker.bash_result(args, working_dir=self.working_dir)


    @staticmethod
    def docker_compose(args, detach=False, working_dir=None):
        """$ docker-compose [args]"""
        if not detach:
            return subprocess.call(
                ["docker-compose"] + args,
                cwd=working_dir,
            )

        proc = subprocess.Popen(
            ["docker-compose"] + args,
            cwd=working_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        return proc


    def docker_compose_cwd(self, args, detach=False):
        """$ docker-compose [args], from directory of current service"""
        return CommandInvoker.docker_compose(
            args,
            detach=detach,
            working_dir=self.working_dir,
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
        return CommandInvoker.docker(args, working_dir=self.working_dir)


    def from_store(self, key):
        """get val by key from persistent storage"""
        data_store = shelve.open(self.data_store_file)
        val = None
        if key in data_store:
            val = data_store[key]
        data_store.close()
        return val


    def to_store(self, key, val):
        """set key:val in persistent storage"""
        data_store = shelve.open(self.data_store_file)
        data_store[key] = val
        data_store.close()


    def set_service(self, service):
        """set the active docker-compose service"""
        local_compose = local_compose_yaml()
        if local_compose is None:
            raise ConfigError("docker-compose.yaml not found in current directory.")
        if not "services" in local_compose:
            raise ConfigError("no 'services' section found in docker-compose.yaml")
        if not service in local_compose["services"]:
            raise ConfigError("no service \"{}\" in docker-compose.yaml".format(service))

        self.service = service
        self.working_dir = Path.cwd()
        self.to_store("service", service)
        self.to_store("working_dir", Path.cwd())
