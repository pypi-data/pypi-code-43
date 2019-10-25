"""class: ServiceInitiailizer"""
# pylint: disable=too-many-branches
import sys
from pathlib import Path

import click

from . import log_printer as log
from ..filesystem.compose_writer import ComposeWriter
from ..filesystem.f_utils import read_compose_yaml
from ..http.dockerhub_api import DockerhubApi
from ..errors import InitializationError


class ServiceInitializer():
    """handles the initialization of a new docker-compose service"""

    def __init__(self):
        """check current directory for existing docker-compose.yaml"""
        self.service_writer = ComposeWriter()

        log.notify("initializing a new dockerized service\n")

        self.local_compose = read_compose_yaml()
        if self.local_compose is None:
            log.notify("Configuration file not found in current directory.")
            if not click.confirm("Generate new docker-compose.yaml?"):
                log.notify("Service initialization terminated.")
                sys.exit()
            with open("./docker-compose.yaml", "w") as docker_compose:
                docker_compose.write('version: "3.7"\nservices:')
            self.local_compose = read_compose_yaml()
            log.success("created new docker-compose.yaml")
        else:
            log.success("detected local docker-compose.yaml")

        self.dockerhub_api = DockerhubApi()


    def confirm(self):
        """print all service information and confirm with user"""
        log.notify("\nCreating Service {}".format(self.service_writer.name))
        log.notify("{:12} {}".format("name", self.service_writer.name), indent_depth=1)

        log.notify("{:12} {}".format(
            "directory",
            self.service_writer.directory.resolve(),
        ), indent_depth=1)

        mount_string = "none"
        if self.service_writer.bind_mount:
            mount_string = "{} -> {}".format(
                self.service_writer.mount_source.resolve(),
                self.service_writer.mount_target,
            )
        log.notify(
            "{:12} {}".format(
                "mount",
                mount_string,
            ),
            indent_depth=1,
        )

        log.notify(
            "{:12} {}".format(
                "base image",
                self.service_writer.base_image,
            ), indent_depth=1,
        )

        log.notify(
            "{:12} {}".format(
                "default shell",
                self.service_writer.default_shell,
            ), indent_depth=1,
        )

        if self.service_writer.gen_dockerfile:
            log.notify(
                "generating {}".format(
                    self.service_writer.directory.resolve()/"Dockerfile"
                ),
                indent_depth=1,
            )

        if self.service_writer.share_ssh_auth:
            log.notify("sharing host ssh authentication", indent_depth=1)

        if self.service_writer.share_x11:
            log.notify("sharing Xhost with service", indent_depth=1)

        if self.service_writer.keep_alive:
            log.notify("keeping service container alive", indent_depth=1)

        if self.service_writer.set_ros_logs:
            log.notify("setting up ros logging directories", indent_depth=1)

        if self.service_writer.use_env:
            log.notify("importing env vars from ./.env", indent_depth=1)

        if not click.confirm("\nProceed?", default=True):
            sys.exit()


    def generate(self) -> str:
        """use user-entered info to initiailze a docker-compose service"""
        self.service_writer.write_service_to_config()
        self.service_writer.write_dockerfile()
        if not self.service_writer.name:
            raise InitializationError("Unexpected: new service has no name.")
        return self.service_writer.name


    def prompt(self):
        """collect and store service info from user"""
        while not self.service_writer.name:
            service_name = click.prompt("service name", type=str)
            if "services" in self.local_compose and \
               self.local_compose["services"] and \
               service_name in self.local_compose["services"]:
                log.error("naming service", "service {} already exists".format(service_name))
            else:
                self.service_writer.name = service_name

        while not self.service_writer.directory:
            directory = click.prompt(
                "service directory",
                default="./{}".format(self.service_writer.name),
                type=click.Path(exists=False),
            )
            directory_path = Path(directory)
            if not directory_path.exists():
                Path.mkdir(directory_path)
                log.success(
                    "created directory {} for new service {}".format(
                        directory_path,
                        self.service_writer.name,
                    ),
                )
                self.service_writer.directory = Path(directory)
            elif not directory_path.is_dir():
                log.error(
                    "setting service directory",
                    "{} is not a directory".format(directory_path),
                )
            elif (directory_path/"entrypoint.sh").exists() or \
                 (directory_path/"Dockerfile").exists():
                log.error(
                    "setting service directory",
                    "{} is already an initialized service directory".format(directory_path),
                )
            else:
                self.service_writer.directory = Path(directory)
                log.success(
                    "using directory {} for new service {}".format(
                        directory_path,
                        self.service_writer.name,
                    ),
                )

        if click.confirm("Mount a host directory into the container?", default=True):
            self.service_writer.bind_mount = True
            log.notify("Configuring mounted directory")
            mount_source = click.prompt(
                log.indent("source (host directory)", 1),
                default="./",
                type=click.Path(
                    exists=True,
                    file_okay=False,
                    dir_okay=True,
                    allow_dash=False
                ),
            )
            self.service_writer.mount_source = Path(mount_source)

            mount_target = click.prompt(
                log.indent("target (container directory)", 1),
                default="/home/matic/{}".format(self.service_writer.name),
                type=click.Path(exists=False),
            )
            self.service_writer.mount_target = Path(mount_target)
        else:
            self.service_writer.bind_mount = False


        log.notify('\nRecent Docker images:')
        tags = self.dockerhub_api.tags(
            org="matician",
            repo="core",
        )
        log.options(
            tags,
            label_prop="name",
            label_prefix="core:",
            extra_option="other",
        )

        # default has to be a string, or typechecker complains. However, type=int doesn't actually
        # cast "default" to an int (like it does for user input) for the following comparison
        # throws a typeerror. So, we manually cast the result to an int
        image_choice = click.prompt(
            "base image",
            default="0",
            type=int,
        )
        image_choice = int(image_choice)
        if 0 <= image_choice <= 9:
            self.service_writer.base_image = "matician/core:{}".format(tags[image_choice]["name"])
        else:
            self.service_writer.base_image = click.prompt("alternative base image", type=str)

        self.service_writer.default_shell = click.prompt(
            "default shell",
            default="bash",
            type=str,
        )

        self.service_writer.gen_dockerfile = click.confirm("generate Dockerfile", default=False)
        self.service_writer.share_ssh_auth = click.confirm("share host ssh auth", default=False)
        self.service_writer.share_x11 = click.confirm("share Xhost", default=True)
        self.service_writer.keep_alive = click.confirm("keep service alive", default=True)
        self.service_writer.set_ros_logs = click.confirm("set up ros logging dirs", default=False)
        self.service_writer.use_env = click.confirm("load env vars from .env", default=True)
        self.service_writer.set_host_uid = click.confirm("set matic UID to host UID", default=True)
        if "volumes" in self.local_compose and \
           self.local_compose["volumes"] and \
           "data" in self.local_compose["volumes"]:
            log.success("detected data volume in local docker-compose.yaml")
            self.service_writer.use_data_volume = click.confirm("mount data volume", default=True)
