# -*- coding: utf-8 -*-
""" Commands related directly to scaffolds (create, apply, etc.) """
from __future__ import absolute_import, unicode_literals

from os.path import abspath, basename

# 3rd party imports
import click
from six import string_types

# local imports
from scaffy import scaffold
from scaffy.core import log
from scaffy.core import git
from . import cli


ArgDirPath = click.Path(file_okay=False, dir_okay=True, exists=True)
ArgScaffold = click.Choice([x.name for x in scaffold.LocalStore().scaffolds])


def marker_def(string):
    """ A simple parameter type to define scaffold markers.

    This will parse a marker in format 'name=value[,other]' to a tuple
    (str, str) of name/value pairs. If there are multiple values, the second
    element in the tuple will be a list of string
    """
    name, value = string.split('=')
    name = name.strip()
    value = value.strip()

    if ',' in value:
        value = value.split(',')

    return name, value


@cli.command('create')
@click.argument('name', type=str, required=True,)
@click.argument('src_dir', type=ArgDirPath)
@click.option(
    '-e',
    '--exclude',
    multiple=True,
    metavar='PATTERN',
    help=('Exclude patterns. To specify multiple patters supply this option '
          'multiple times.')
)
@click.option(
    '-m', '--marker', 'markers',
    type=marker_def,
    multiple=True,
    metavar='NAME=VALUE(S)',
    help=('Markers that will be created in the scaffold. Supply each marker '
          'using -m name=value1,value2 format. In the above example, every '
          "occurrence of either 'value1' or 'value2' will be replaced with "
          "marker named 'name'. The marker will be replaced with real value "
          "when the scaffold is applied (a project is generated)."
          "This also applies to file and directory names.")
)
@click.option(
    '--no-gitignore',
    is_flag=True,
    help='If given, .gitignore will not be read for exclude patterns.'
)
@click.option(
    '-v', '--verbose',
    count=True,
    help="Be more verbose."
)
def create(name, src_dir, markers, exclude, no_gitignore, verbose):
    """ Create new scaffold from a source directory.

    This command will create a new scaffold with the given name from the
    supplied src_dir. A template is just a collection of files, some of them
    with markers. The markers are generated during the scaffold creation (this
    command) and later replaced with real values when the apply command is used.

    The scaffold is created in the local store. To list all scaffolds in the
    local store, use scaffy list. It can also be pushed to scaffy hub so it
    can be accessed from any machine.

    Example:

        \033[1mscaffy create my-scaffold . -e dist -e build \033[0m

    The above call will create a scaffold with name 'my-scaffold' and contents
    of the current directory except for files/dirs matching 'dist' and 'build'
    """
    log.info("Creating scaffold ^35{}".format(name))

    store = scaffold.LocalStore()

    markers = dict(markers)
    markers.setdefault('name', basename(abspath(src_dir)))

    if verbose:
        log.info("Exclude")
        for pattern in sorted(exclude):
            log.info("    ^0{}", pattern)

    if not no_gitignore:
        git_exclude = git.load_gitignore(src_dir)
        exclude = set(exclude) | set(git_exclude) | {'.git'}

        if verbose:
            log.info("Exclude from .gitignore")
            for pattern in sorted(git_exclude):
                log.info("    ^0{}", pattern)

    if name is None:
        name = markers['name']
        if not isinstance(name, string_types):
            name = name[0]      # name is a list of names, pick the first one.

    item = scaffold.Scaffold.create(src_dir, name, exclude, markers)
    store.add(item)


@cli.command('apply')
@click.argument('name', type=ArgScaffold)
@click.argument('project_name', type=str)
@click.option(
    '-o', '--out-path',
    type=ArgDirPath,
    default='.',
    help=("Specify the path where the new project will be created. The"
          "project folder will be created within the given path.")
)
def apply_scaffold(name, project_name, out_path):
    """ Generate project using the given scaffold.

    The project will have all the scaffold contents with 'name' markers replaced
    by project_name. Be default, the project folder will be created inside the
    current working directory. This can be changed using the --out-path option.
    """
    store = scaffold.LocalStore()
    item = store.load(name)
    item.apply(project_name, out_path)
