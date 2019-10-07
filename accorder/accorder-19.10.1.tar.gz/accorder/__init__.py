import click
import readline
import os
import sys
from accorder.utils.configurations import run_configuration
from accorder.utils.uploads import run_upload
from accorder.utils.submits import run_submit
from accorder.utils.builds import run_build
from collections import OrderedDict

APP_NAME = "accorder"

# ---------------------------------------
# readline path completion by johann woelper
# from: https://schdbr.de/python-readline-path-completion/


def list_folder(path):
    if path.startswith(os.path.sep):
        basedir = os.path.dirname(path)
        contents = os.listdir(basedir)
        contents = [os.path.join(basedir, d) for d in contents]
        contents = [d + os.path.sep for d in contents if os.path.isdir(d)]
    else:
        contents = os.listdir(os.curdir)
        contents = [d + os.path.sep for d in contents if os.path.isdir(d)]
    return contents


def completer(text, state):
    options = [x for x in list_folder(text) if x.startswith(text)]
    return options[state]


readline.set_completer(completer)

if sys.platform == "darwin":
    # readline.parse_and_bind("bind -e")
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")
    readline.set_completer_delims(" \t\n`~!@#$%^&*()-=+[{]}\\|;:'\",<>?")
# end of readline


# ---------------------------------------
# click stuff


class NaturalOrderGroup(click.Group):
    def __init__(self, name=None, commands=None, **attrs):
        if commands is None:
            commands = OrderedDict()
        elif not isinstance(commands, OrderedDict):
            commands = OrderedDict(commands)
        click.Group.__init__(self, name=name, commands=commands, **attrs)

    def list_commands(self, ctx):
        return self.commands.keys()


def get_version():
    import pkg_resources

    return pkg_resources.get_distribution("accorder").version


@click.group(cls=NaturalOrderGroup)
@click.version_option(version=get_version())
def cli():
    """Accorder takes care of various tasks which Memory of the World amateur librarians do in order to maintain their shared catalogs online.\n
    It builds searchable, standalone, portable webapp which one could then just copy to USB disk and open BROWSE_LIBRARY.html in her web browser.\n
    It uploads all of the books and metadata from local Calibre's library (together with portable webapp) to the server.\n
    It helps a librarian to maintain and share her catalog at https://library.memoryoftheworld.org together with other amateur librarians.\n
    It does all of above in one go by typing: accorder release PROFILE.\n
    The configuration file will keep information about one or more PROFILE. Under every PROFILE's configuration section there will be information about the directory path of local Calibre's library, librarian's name, credentials needed to upload the files to the destination server etc.
    """
    pass


@cli.command(
    short_help="Manage configuration. For more help, type: accorder configuration --help"
)
@click.argument("configuration_id", required=False)
@click.option(
    "--show", "-s", help="Show summary from the configuration file.", is_flag=True
)
@click.option(
    "--replace",
    "-r",
    help="Replace current configuration with the new one set by CONFIGURATION_ID. This flag requires CONFIGURATION_ID to be provided. (e.g: `accorder configuration --replace CONFIGURATION_ID``)",
    is_flag=True,
)
def configuration(configuration_id, show, replace):
    run_configuration(APP_NAME, configuration_id, show, replace)


@cli.command(
    short_help="Build standalone, portable webapp against the local Calibre library. For more help, type: accorder build --help"
)
@click.argument("profile")
@click.option(
    "--directory",
    "-d",
    help="Add/change PROFILE's directory path (of Calibre library) for the standalone, portable webapp to be built including all the metadata needed. Once provided, the directory path is automatically saved into configuration file for the future use.",
    type=click.Path(exists=True, resolve_path=True, file_okay=False),
)
@click.option(
    "--librarian",
    "-l",
    help="Add/change librarian's name (max. 42 chars) for the given PROFILE. Once provided, librarian's name is automatically saved into configuration file for the future use.",
)
def build(profile, directory, librarian):
    """Build searchable, standalone, portable webapp against the local Calibre library including all the metadata needed. It creates BROWSE_LIBRARY.html in root directory of the local Calibre library. For search (authors, titles, tags...) it uses rendered metadata from static/data.js file.\n
    If the local Calibre's library directory path is not already provided in the configuration file `accorder` will ask you to provide it (TAB completion should work).
    The same directory path could be anytime changed by using the flag (-d, --directory). For example:\n
    accorder build -d /your/path/to/calibre/library/ PROFILE\n
    Every time the directory path is provided it is saved in configuration file for the future use (therefore: `accorder build PROFILE` should be enough for the successful build).
"""
    run_build(APP_NAME, profile, directory, librarian)


@cli.command(
    short_help="Upload the Calibre collection to the Memory of the World Library. For more help, type: accorder upload --help"
)
@click.argument("profile")
@click.option(
    "--directory",
    "-d",
    help="Add/change PROFILE's directory path to be uploaded to the server. The directory path is automatically saved into configuration file for the future use.",
    type=click.Path(exists=True, resolve_path=True, file_okay=False),
)
@click.option(
    "--delete-residue",
    help="Delete any remote directories/files which are not present locally anymore.",
    is_flag=True,
)
def upload(profile, directory, delete_residue):
    """Upload the Calibre collection to the Memory of the World server. Rsync (or rclone) will only upload local files which are missing at (or different from) the remote destination at the Memory of the World server.\n
    If the local Calibre's library directory path is not already provided in the configuration file `accorder` will ask you to provide it (TAB completion should work).
    The same directory path could be anytime changed by using the flag (-d, --directory). For example:\n
    accorder upload -d /your/path/to/calibre/library/ PROFILE\n
    Every time the directory path is provided it is saved in configuration file for the future use (therefore: `accorder upload PROFILE` should be enough for the successful upload).
    """
    run_upload(APP_NAME, profile, directory, delete_residue)


@cli.command(
    short_help="Maintain the shared Calibre's collection at the Memory of the World Library. For more help: accorder submit --help"
)
@click.argument("profile")
@click.option(
    "--librarian",
    "-l",
    help="Add/change librarian's name (max. 42 chars) for the given PROFILE. Once provided, librarian's name is automatically saved into configuration file for the future use.",
)
@click.option(
    "--off",
    help="Take PROFILE's library off from the Memory of the World Library.",
    is_flag=True,
)
def submit(profile, librarian, off):
    """Submit all the local (metadata) changes for PROFILE's Calibre collection to the Memory of the World Library (https://library.memoryoftheworld.org)"""
    run_submit(APP_NAME, profile, librarian, off)


@cli.command(
    short_help="Release local Calibre collection to the Memory of the World Library. For more help, type: accorder release --help"
)
@click.argument("profile")
@click.option(
    "--directory",
    "-d",
    help="Add/change PROFILE's directory path to be uploaded to the server. It is automatically saved into configuration file for the future use.",
    type=click.Path(exists=True, resolve_path=True, file_okay=False),
)
@click.option(
    "--librarian",
    "-l",
    help="Add/change librarian's name (max. 42 chars) for the given PROFILE. Once provided, librarian's name is automatically saved into configuration file for the future use.",
)
@click.option(
    "--delete-residue",
    help="Delete any remote directories/files which are not present locally anymore.",
    is_flag=True,
)
@click.option(
    "--off",
    help="Take PROFILE's library off from the Memory of the World Library.",
    is_flag=True,
)
def release(profile, directory, librarian, delete_residue, off):
    """Release PROFILE's Calibre collection to the Memory of the World Library. First, it builds locally the standalone portable webapp (as if `accorder build PROFILE` was run), then it uploads all the files to the server (`accorder upload PROFILE`) and finally it submits all the metadata to the Memory of the World Library (`accorder submit PROFILE`)."""
    run_build(APP_NAME, profile, directory, librarian)
    run_upload(APP_NAME, profile, directory, delete_residue)
    run_submit(APP_NAME, profile, librarian, off)


if __name__ == "__main__":
    cli()
