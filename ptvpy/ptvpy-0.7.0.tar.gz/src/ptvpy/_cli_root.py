"""Root of the command line interface."""


import os
import warnings

import click

from . import __version__
from ._cli_export import export_command
from ._cli_generate import generate_group
from ._cli_process import process_command
from ._cli_profile import profile_group
from ._cli_view import view_group


def _open_html_documentation(ctx, param, value):
    """Callback for eager option: open online documentation and exit."""
    if not value or ctx.resilient_parsing:
        # Callback is called regardless of the options value so we need to
        # do nothing and return control. See
        # https://click.palletsprojects.com/en/7.x/options/#callbacks-and-eager-options
        return
    url = "https://tud-mst.gitlab.io/ptvpy"
    click.echo(f"Opening '{url}'")
    click.launch(url, wait=False)
    ctx.exit()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--debug",
    help="Enable debug mode (show full traceback, warnings, ...).",
    is_flag=True,
)
@click.version_option(version=__version__)
@click.option(
    "--documentation",
    is_flag=True,
    expose_value=False,
    is_eager=True,
    callback=_open_html_documentation,
    help="Open online documentation and exit.",
)
@click.pass_context
def root_group(ctx, **kwargs):
    """Command line tool for particle tracking velocimetry.

    PtvPy is modularized into several subcommands. Call any subcommand with the help
    option "-h" to show more information.
    """
    if ctx.obj is None:
        ctx.obj = dict()
    if kwargs["debug"]:
        os.environ["PTVPY_DEBUG"] = "1"
    if not os.environ.get("PTVPY_DEBUG"):
        warnings.simplefilter("ignore", FutureWarning)


# Add subcommands manually here. We could use root_group.group / root_group.command to
# do this implicitly but this would require this module and the submodule to depend on
# each other. While circular imports are solvable with delayed imports (e.g. at the end
# of this module), this would lead to import errors when this module wasn't imported
# first. This way we have a nice dependency graph without circular imports.
root_group.add_command(export_command)
root_group.add_command(generate_group)
root_group.add_command(profile_group)
root_group.add_command(process_command)
root_group.add_command(view_group)


def main(*args, **kwargs):
    """Entry point of the application.

    Parameters
    ----------
    *args, **kwargs
        Same as `click.BaseCommand.main`.

    Notes
    -----
    This function will swallow exceptions unless debug mode is enabled. Enable
    by either setting the environment variable "PTVPY_DEBUG" or by passing
    "--debug" as the first command line option.
    """
    try:
        root_group.main(*args, **kwargs, standalone_mode=False)
    except (KeyboardInterrupt, click.Abort):
        click.secho("\nKeyboard Interrupt", fg="red")
    except Exception as error:
        # If Debug mode is enabled, just propagate the error
        if os.environ.get("PTVPY_DEBUG"):
            raise error

        if isinstance(error, click.ClickException):
            # TODO click.MissingParameter.__str__ returns a non string value
            #  should be fixed upstream, until then use its nice formatting method
            msg = error.format_message()
        else:
            msg = str(error)
        click.secho(f"\n{type(error).__name__}: {msg}", fg="red", err=True)

        if hasattr(error, "hint") and error.hint:
            hint = error.hint
        else:
            hint = (
                "Append '-h' for help or retry with 'ptvpy --debug ...' to show the "
                "traceback."
            )
        click.secho("\n" + hint)
        return 1
