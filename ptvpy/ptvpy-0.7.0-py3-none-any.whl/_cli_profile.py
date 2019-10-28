"""Command-group `profile` with subcommands."""


from pathlib import Path

import click

from ._profile import Profile, template_path
from ._cli_utils import AddProfileDetection, LazyImport


difflib = LazyImport("difflib")
_profile = LazyImport(".._profile", package=__name__)


@click.group(name="profile")
def profile_group(**kwargs):
    """Manage profiles.

    This subcommand allows the creation, manipulation and validation of
    profiles. A profile is stored inside a TOML file and tells PtvPy how to
    process or handle a given data set. Only profiles that validate
    successfully against a schema are used.

    Many subcommands of PtvPy are able to autodetect profile files ending with
    ".ptvpy.toml" in the current working directory if no file is
    given explicitly with the "--profile" option.
    """
    pass


@profile_group.command(name="create")
@click.option(
    "--path",
    help="Create a profile at the given path. Default: "
    f"{_profile.DEFAULT_PROFILE_NAME}",
    type=click.Path(exists=False, dir_okay=False),
    default=_profile.DEFAULT_PROFILE_NAME,
)
@click.option(
    "--data-files",
    type=click.STRING,
    help="A pattern matching the image files to process. Default: '*.tif*'",
    default="*.tif*",
)
def create_command(**kwargs):
    """Create a new profile."""
    # Use default name if not supplied
    path = Path(kwargs["path"] or _profile.DEFAULT_PROFILE_NAME)
    if path.is_file():
        raise FileExistsError(f"already exists: {path}")
    _profile.create_profile_file(path, kwargs["data_files"])
    click.echo(f"Created '{path}'")
    profile = _profile.Profile(path)
    if not profile.is_valid:
        click.secho("\nWarning: " + profile.report_validation(), fg="red")


@profile_group.command(name="check")
@click.option(
    "--pattern",
    help="Specify the pattern to check against. Default: "
    f"{_profile.Profile.DEFAULT_PATTERN}",
    type=click.STRING,
    default=_profile.Profile.DEFAULT_PATTERN,
)
def check_command(pattern):
    """Check for valid profiles in a directory."""
    click.echo(f"Checking files matching '{Path(pattern)}':")
    profiles = _profile.Profile.from_pattern(pattern)
    if profiles:
        for p in profiles:
            fg = "green" if p.is_valid else "red"
            click.secho("\n" + p.report_validation(), fg=fg)
    else:
        click.secho("\nno matching files", fg="red")
    click.echo()


@profile_group.command(name="edit")
@AddProfileDetection(validation=False)
def edit_command(profile):
    """Open profile in default editor for TOML files.

    This will open the given/detected profile inside the text editor associated with
    TOML files.
    """
    click.launch(str(profile.path), wait=False)


@profile_group.command(name="diff")
@click.argument("file", type=click.Path(exists=True, dir_okay=False), nargs=-1)
def diff_command(file):
    """Compare profiles.

    Use this to see which configuration values differ between profiles or the template
    (profile with default values).

    Compares the content of two files (usually profiles) using the unified diff format.
    For convenience, this command tries to guess the files to compare if no or only 1
    file path is specified:
    If no file is given, it will try to autodetect one profile in the current directory
    and compare it with the template.
    If only 1 file is given, its content will be compared with the default profile
    (template) as well.
    2 files will be compared directly.
    """
    if len(file) == 0:
        file = (
            template_path(),
            AddProfileDetection.detect_profile(Profile.DEFAULT_PATTERN).path,
        )
    elif len(file) == 1:
        file = (template_path(), file[0])
    elif len(file) == 2:
        pass
    else:
        raise click.BadArgumentUsage(
            f"to many arguments: expected 0-2, got {len(file)}"
        )
    file = tuple(str(f) for f in file)  # Ensure consistent types

    with open(file[0], "r") as stream:
        first = stream.readlines()
    with open(file[1], "r") as stream:
        second = stream.readlines()
    diff = list(difflib.unified_diff(first, second, fromfile=file[0], tofile=file[1]))
    if not diff:
        click.echo(f'"{file[0]}" and "{file[1]}" are identical')
        return
    fg_map = {"-": "red", "+": "green", "@": "magenta"}
    for line in diff:
        click.secho(line, fg=fg_map.get(line[0]), nl=False)
    click.echo()
