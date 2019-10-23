"""
Adapted from https://github.com/bmwant/podmena/blob/master/podmena/cli.py
"""

import configparser
import os
import shutil
import sys

import click

from whatcha_readin.config import VERSION
from whatcha_readin.utils import _warn, _note
from whatcha_readin.paths import WhatchaReadinPaths


@click.group()
@click.version_option(version=VERSION, prog_name="whatcha-readin")
def cli():
    pass


@cli.command(
    name="status", help="Shows whether whatcha-readin is activated for this repository"
)
def status() -> None:
    active = False

    git_root_dir = WhatchaReadinPaths.get_git_root_dir()
    if git_root_dir is not None:
        hook_path = WhatchaReadinPaths.get_hook_path()
        if os.path.exists(hook_path):
            _note("whatcha-readin is activated for this repository!")
            active = True

    if not active:
        _warn("whatcha-readin is not activated for this repository")


@cli.command(name="install", help="Install whatcha-readin for current git repository")
def install() -> None:
    git_root_dir = WhatchaReadinPaths.get_git_root_dir()
    if git_root_dir:
        # copy our hook file over
        src_file = WhatchaReadinPaths.get_src_hook_path()
        dst_file = WhatchaReadinPaths.get_hook_path()
        shutil.copyfile(src_file, dst_file)
        os.chmod(dst_file, 0o0775)
        _note(
            """Successfully installed for this repository!
            \nPlease configure goodreads access with `whatcha-readin configure`"""
        )
    else:
        _warn("Not a git repository")
        sys.exit(1)


def is_installed() -> bool:
    hook_filepath = WhatchaReadinPaths.get_hook_path()
    return os.path.exists(hook_filepath)


@cli.command(
    name="uninstall", help="Uninstall whatcha-readin for current git repository"
)
def uninstall() -> None:
    if is_installed():
        hook_filepath = WhatchaReadinPaths.get_hook_path()
        config_path = WhatchaReadinPaths.get_config_path()
        os.remove(hook_filepath)
        if os.path.exists(config_path):
            os.remove(config_path)
        _note("Uninstalled for current repository")
    else:
        _warn("whatcha-readin is not installed for current repository!")
        sys.exit(1)


@cli.command(name="config", help="configure your goodreads user by ID")
@click.option("--user-id", prompt="Your goodreads user ID", required=True)
@click.option("--key", prompt="Your goodreads API key", required=True)
def configure_goodreads_access(user_id: str, key: str) -> None:
    # TODO: can this be called before prompting?
    if not is_installed():
        _warn(
            "Cannot configure without installing first. "
            "Please run `whatcha-readin install`"
        )
        sys.exit(1)

    config = configparser.ConfigParser()
    config["GOODREADS"] = {"api_key": key, "user_id": user_id}

    config_path = WhatchaReadinPaths.get_config_path()
    with open(config_path, "w") as f:
        config.write(f)

    _note("Successfully configured goodreads access!")


if __name__ == "__main__":
    cli()
