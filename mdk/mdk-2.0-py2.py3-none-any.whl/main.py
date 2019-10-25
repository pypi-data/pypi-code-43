"""mdk is a docker-compose helper"""
# pylint: disable=unused-argument
import click
import pkg_resources

from .cli.shell_invoker import ShellInvoker
from .cli.commands import define_commands


VERSION = pkg_resources.require("mdk")[0].version


def main(*args, **kwargs):
    """set up and execute the mdk cli"""
    @click.group()
    @click.version_option(version=VERSION)
    @click.pass_context
    def cli(ctx, prog_name="mdk"):
        """docker/docker-compose helper and taskrunner"""
        ctx.obj = ShellInvoker()

    pass_invoker = click.make_pass_decorator(ShellInvoker, ensure=True)

    define_commands(cli.command, pass_invoker)

    cli(*args, **kwargs)
