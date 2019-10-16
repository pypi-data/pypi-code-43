"""Custom exceptions mostly for handling validation errors (e.g. missing
worksheet or columns)."""

# --- Standard Library Imports ------------------------------------------------
import collections
import functools

# --- Third Party Imports -----------------------------------------------------
import click
import requests

# --- Intra-Package Imports ---------------------------------------------------
from rtm import __version__ as installed_version
from rtm.containers.markup import CellMarkup


@functools.lru_cache()
def get_versions():
    """Return tuple of installed and pypi version numbers."""
    Versions = collections.namedtuple("Versions", "installed pypi")
    response = requests.get("https://pypi.org/pypi/dps-rtm/json")
    return Versions(
        installed=installed_version,
        pypi=response.json()['info']['version'],
    )


def get_version_check_message():
    versions = get_versions()
    if versions.pypi == versions.installed:
        return [
            CellMarkup(f"Your app is up to date ({versions.installed})"),
        ]
    else:
        return [
            CellMarkup("Your app is out of date.", is_error=True),
            CellMarkup(f"Currently installed: {versions.installed}", indent=True),
            CellMarkup(f"Available: {versions.pypi}", indent=True),
            CellMarkup("Upgrade to the latest by entering the following:", indent=True),
            CellMarkup("pip install --upgrade dps-rtm", indent=True),
        ]


def print_version_check_message():
    """Command Line Output: is app up to date?"""
    for line in get_version_check_message():
        if line.is_error:
            click.secho(line.comment, fg='red', bold=True,)
        else:
            click.echo(line.comment)
