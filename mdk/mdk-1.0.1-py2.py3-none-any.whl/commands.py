"""define all mdk cli commands"""
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=unused-variable
import sys
from typing import Callable

import click

from . import errors
from . import log_printer
from .command_invoker import CommandInvoker
from .service_initializer import ServiceInitializer


def define_commands(mdk_command: Callable[..., Callable], pass_invoker: Callable):
    """define all mdk cli commands"""
    @mdk_command(
        name="bash",
        short_help="attach a bash shell for the active, running service",
    )
    @pass_invoker
    def mdk_bash(invoker):
        """attach a bash shell for the active, running service

        docker-compose exec SERVICE bash"""
        if not invoker.service:
            log_printer.error("attaching bash", "No active service. Try \"mdk use SERVICE\"")
            sys.exit(0)

        invoker.docker_compose_cwd(["exec", invoker.service, "bash"])


    @mdk_command(
        name="build",
        short_help="build the current service",
    )
    @pass_invoker
    def mdk_build(invoker):
        """Build the active service

        docker-compose build SERVICE"""
        if not invoker.service:
            log_printer.error("building service", "No active service. Try \"mdk use SERVICE\"")
            sys.exit(0)
        invoker.docker_compose_cwd(["build", invoker.service])


    @mdk_command(
        context_settings={"ignore_unknown_options": True},
        name="dc",
        short_help="run a docker-compose command",
    )
    @click.argument("command", nargs=-1, type=click.STRING)
    def mdk_dc(command):
        """Passthrough for running docker-compose commands

        docker-compose COMMAND"""
        CommandInvoker.docker_compose(list(command))


    @mdk_command(
        name="down",
        short_help="start a container for the current service",
    )
    @pass_invoker
    def mdk_down(invoker):
        """stop and remove service containers for *all* services in active docker-compose.yaml

        docker-compose down"""
        if not invoker.service:
            log_printer.error("building service", "No active service. Try \"mdk use SERVICE\"")
            sys.exit(0)
        if not click.confirm(
                "\nDestroying containers for active service {}\nProceed?".format(invoker.service),
                default=True):
            sys.exit(0)
        invoker.docker_compose_cwd(["down"])


    @mdk_command(
        context_settings={"ignore_unknown_options": True},
        name="dr",
        short_help="run a docker command",
    )
    @click.argument("command", nargs=-1, type=click.STRING)
    def mdk_dr(command):
        """Passthrough for running docker commands

        docker COMMAND"""
        CommandInvoker.docker(list(command))


    @mdk_command(
        name="init",
    )
    @pass_invoker
    def mdk_init(invoker):
        """Initialize a new docker-compose service"""
        try:
            initializer = ServiceInitializer()
            initializer.prompt()
            initializer.confirm()
            service_name = initializer.generate()
            invoker.set_service(service_name)
        except errors.InitializationError as err:
            log_printer.error("initializing new service", err.message)
        else:
            log_printer.success("{} initiailized. Launch service:".format(service_name))
            log_printer.notify("mdk up\n", indent_depth=2)


    @mdk_command(
        name="down",
        short_help="view container logs",
    )
    @pass_invoker
    def mdk_logs(invoker):
        """"view container logs

        docker-compose logs SERVICE
        """
        if not invoker.service:
            log_printer.error("viewing service logs", "No active service. Try \"mdk use SERVICE\"")
            sys.exit(0)

        invoker.docker_compose_cwd(["logs", invoker.service])


    @mdk_command(
        name="lsi",
        short_help="list all docker images",
    )
    @click.option("-v", "--verbose", is_flag=True)
    def mdk_lsi(verbose):
        """list all docker images

        docker images"""
        images_command = ["images"]
        if not verbose:
            images_command.extend([
                "--format",
                "table {{.Repository}}\t{{.Tag}}\t{{.Size}}",
            ])
        CommandInvoker.docker(images_command)


    @mdk_command(
        name="lsc",
        short_help="list all docker containers",
    )
    @click.option("-v", "--verbose", is_flag=True)
    def mdk_lsc(verbose):
        """list all docker containers

        docker ps -a"""
        ls_command = ["ps", "-a"]
        if not verbose:
            ls_command.extend([
                "--format",
                "table {{.Names}}\t{{.Image}}\t{{.Status}}",
            ])
        CommandInvoker.docker(ls_command)


    @mdk_command(
        name="exec",
        short_help="run a command using the active service",
    )
    @click.argument("command", nargs=-1, type=click.STRING)
    @click.option("-d", "--detach", is_flag=True)
    @pass_invoker
    def mdk_exec(invoker, command, detach):
        """run a command using the active service

        docker-compose exec [-d] SERVICE COMMAND"""
        if not invoker.service:
            log_printer.error("executing command", "No active service. Try \"mdk use SERVICE\"")
            sys.exit(0)

        exec_command = ["exec", invoker.service]
        invoker.docker_compose_cwd(exec_command + list(command), detach=detach)
        if detach:
            log_printer.success("Executed {} with service {}".format(
                " ".join(command),
                invoker.service,
            ))


    @mdk_command(
        name="pause",
        short_help="pause a running container for the current service",
    )
    @pass_invoker
    def mdk_pause(invoker):
        """"pause a running container for the current service

        docker-compose pause SERVICE
        """
        if not invoker.service:
            log_printer.error("pausing service", "No active service. Try \"mdk use SERVICE\"")
            sys.exit(0)

        invoker.docker_compose_cwd(["pause", invoker.service])


    @mdk_command(
        name="prune",
    )
    @click.option("-v", "--volumes", is_flag=True)
    def mdk_prune(volumes):
        """remove dangling docker assets (containers, images, and (optionally) volumes)"""
        prune_command = ["system", "prune", "-a", "-f"]
        action_string = "Destroying all inactive containers and unused images."
        if volumes:
            prune_command.append("--volumes")
            action_string = "Destroying all inactive containers, volumes, and unused images."
        if not click.confirm("\n{}\nProceed?".format(action_string), default=True):
            sys.exit(0)

        CommandInvoker.docker(prune_command)


    @mdk_command(
        name="run",
        short_help="Run a one-time command for the active service",
    )
    @click.argument("command", nargs=-1, type=click.STRING)
    @pass_invoker
    def mdk_run(invoker, command):
        """Run a one-time command for the active service

        docker-compose run SERVICE COMMAND"""
        if not invoker.service:
            log_printer.error("running service", "No active service. Try \"mdk use SERVICE\"")
            sys.exit(0)

        run_command = ["run", invoker.service]

        invoker.docker_compose_cwd(run_command + list(command))


    @mdk_command(
        name="start",
        short_help="start an existing container for the current service",
    )
    @pass_invoker
    def mdk_start(invoker):
        """"start an existing container for the current service

        docker-compose start SERVICE"""
        if not invoker.service:
            log_printer.error("starting service", "No active service. Try \"mdk use SERVICE\"")
            sys.exit(0)

        invoker.docker_compose_cwd(["start", invoker.service])


    @mdk_command(
        name="status",
    )
    @pass_invoker
    def mdk_status(invoker):
        """print the current active service"""
        if invoker.service and invoker.working_dir:
            log_printer.notify("active service:")
            log_printer.notify("{:8}{}".format("name", invoker.service), indent_depth=2)
            log_printer.notify("{:8}{}".format("root", invoker.working_dir), indent_depth=2)
            log_printer.notify("mdk data store:")
            log_printer.notify("{:8}{}".format("file", invoker.data_store_file), indent_depth=2)
        else:
            log_printer.notify("no active service")


    @mdk_command(
        name="stop",
        short_help="stop running container for the current service",
    )
    @pass_invoker
    def mdk_stop(invoker):
        """stop running container for the current service

        docker-compose stop SERVICE
        """
        if not invoker.service:
            log_printer.error("stopping service", "No active service. Try \"mdk use SERVICE\"")
            sys.exit(0)

        invoker.docker_compose_cwd(["stop", invoker.service])


    @mdk_command(
        name="term",
        short_help="Open up a new detatched alacritty terminal",
    )
    @pass_invoker
    def mdk_term(invoker):
        """Open up a new detatched alacritty terminal
        Only works for dev images with alacritty installed

        docker-compose exec -d SERVICE alacritty
        """
        if not invoker.service:
            log_printer.error("opening terminal", "No active service. Try \"mdk use SERVICE\"")
            sys.exit(0)

        invoker.docker_compose_cwd(["exec", "-d", invoker.service, "alacritty"])


    @mdk_command(
        name="unpause",
        short_help="unpause a paused container for the current service",
    )
    @pass_invoker
    def mdk_unpause(invoker):
        """"unpause a paused container for the current service

        docker-compose unpause SERVICE
        """
        if not invoker.service:
            log_printer.error("unpausing service", "No active service. Try \"mdk use SERVICE\"")
            sys.exit(0)

        invoker.docker_compose_cwd(["unpause", invoker.service])


    @mdk_command(
        name="use",
    )
    @pass_invoker
    @click.argument(
        "service",
        type=click.STRING,
    )
    def mdk_use(invoker, service):
        """Set the active docker-compose service"""
        try:
            invoker.set_service(service)
        except errors.ConfigError as err:
            log_printer.error("setting active service to \"{}\"".format(service), err.message)
        else:
            log_printer.success("New active service: {}".format(service))


    @mdk_command(
        name="up",
        short_help="start a container for the current service",
    )
    @pass_invoker
    @click.option("-a", "--attach", is_flag=True)
    @click.option("-b", "--build", is_flag=True)
    @click.option("--bash", is_flag=True)
    def mdk_up(invoker, attach, build, bash):
        """Start a container for the active service

        docker-compose up [--build] [-d] SERVICE"""
        if not invoker.service:
            log_printer.error("starting service", "No active service. Try \"mdk use SERVICE\"")
            sys.exit(0)

        up_command = ["up"]
        if build:
            up_command.append("--build")
        if not attach:
            up_command.append("-d")
        up_command.append(invoker.service)
        invoker.docker_compose_cwd(up_command)
        if bash:
            invoker.docker_compose_cwd(["exec", invoker.service, "bash"])


    @mdk_command(
        name="zsh",
        short_help="attach a zsh shell for the active, running service",
    )
    @pass_invoker
    def mdk_zsh(invoker):
        """attach a zsh shell for the active, running service

        docker-compose exec SERVICE bash"""
        if not invoker.service:
            log_printer.error("attaching zsh", "No active service. Try \"mdk use SERVICE\"")
            sys.exit(0)

        invoker.docker_compose_cwd(["exec", invoker.service, "zsh"])
