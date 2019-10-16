"""This is pretty boiler plate right now. Later, as more command line options
are added in, this module will become more substantial."""

# --- Standard Library Imports ------------------------------------------------
# None

# --- Third Party Imports -----------------------------------------------------
import click

# --- Intra-Package Imports ---------------------------------------------------
from rtm.main import api


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """`rtm` on the command line will run the this function. Later, this will
    have more functionality. That's why it appear superfluous right now"""
    if ctx.invoked_subcommand is None:
        api.main()


@main.command()
@click.option('--original', '-o', is_flag=True)
def markup(original):
    api.main(True, original)
