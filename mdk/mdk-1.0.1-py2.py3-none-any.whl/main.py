"""mdk is a docker-compose helper"""
# pylint: disable=unused-argument
import click

from .command_invoker import CommandInvoker
from .commands import define_commands

def main(*args, **kwargs):
    """set up and execute the mdk cli"""
    @click.group()
    @click.pass_context
    def cli(ctx, prog_name="mdk"):
        """docker/docker-compose helper and taskrunner"""
        ctx.obj = CommandInvoker()

    pass_invoker = click.make_pass_decorator(CommandInvoker, ensure=True)

    define_commands(cli.command, pass_invoker)

    cli(*args, **kwargs)
