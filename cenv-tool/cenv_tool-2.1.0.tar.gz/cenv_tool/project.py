# -*- coding: utf-8 -*-
"""Contain the logic for conda environment creation from ``meta.yaml``.

cenv is a tool to handle conda environment creation and update from the
dependency-definition inside the ``meta.yaml`` file.

As default conda has two files for dependency management:
* the ``environment.yml``
* and the ``meta.yaml``

In the ``environment.yml`` the environment-definition is stored.
In the ``meta.yaml`` the required information to build a conda-package are
stored.
This means redundant information.

cenv collects the dependency-information and all project-specific settings
from the ``meta.yaml``.

The collected information is used to create / update the projects conda
environment.
"""
from argparse import ArgumentParser
from argparse import Namespace
from argparse import RawTextHelpFormatter
from pathlib import Path
from typing import List
from typing import NoReturn

import attr

from cenv_tool import __version__
from cenv_tool.rules import ARGPARSE_DESCRIPTION
from cenv_tool.rules import CondaCmdFormats
from cenv_tool.rules import RULES
from cenv_tool.rules import Rules
from cenv_tool.utils import CenvProcessError
from cenv_tool.utils import extract_dependencies_from_meta_yaml
from cenv_tool.utils import message
from cenv_tool.utils import read_config
from cenv_tool.utils import read_meta_yaml
from cenv_tool.utils import run_in_bash


@attr.s(slots=True, auto_attribs=True)
class Project:
    """Contain a python-project using conda environments.

    Containing methods to display information to current project and methods
    to update the projects conda-environment from the settings defined in the
    projects ``meta.yaml``.
    """

    rules: Rules
    conda_folder: Path = attr.ib(default=None)
    env_folder: Path = attr.ib(default=None)
    env_name: str = attr.ib(default=None)
    dependencies: dict = attr.ib(default=None)
    is_env: bool = attr.ib(default=None)
    export_environment_yml: bool = attr.ib(None)
    cmds: CondaCmdFormats = attr.ib(default=None)
    cmd_kwargs: dict = attr.ib(default=None)
    is_git: bool = attr.ib(default=None)

    def __attrs_post_init__(self):
        """Set the more complex attributes of the project class."""
        try:
            meta_yaml = read_meta_yaml(Path.cwd())
        except FileNotFoundError:
            message(text='project has no meta.yaml!', color='red')
            exit(1)
        settings = meta_yaml['extra']
        dependencies = extract_dependencies_from_meta_yaml(meta_yaml)

        config = read_config()
        self.is_git = (Path.cwd() / self.rules.git_folder).exists()
        self.export_environment_yml = config['export_environment_yml']
        self.conda_folder = Path(config['conda_folder'])
        self.env_folder = Path(config['env_folder'])
        self.env_name = settings['env_name']
        self.dependencies = dependencies
        self.is_env = self.env_name in self.collect_available_envs()
        conda_bin = self.rules.conda_cmds.conda_bin(self.conda_folder)
        self.cmds = self.rules.conda_cmds
        self.cmd_kwargs = {
            'conda': conda_bin,
            'name': self.env_name,
            'pkgs': ' '.join([f'"{_}"' for _ in self.dependencies]),
        }

    def collect_available_envs(self) -> List[str]:
        """Collect the names of the conda environments currently installed.

        Parameters:
            conda_folder: the path where conda is installed.

        Returns:
            list of currently installed conda-environments

        """
        return run_in_bash(
            str(self.conda_folder.absolute()) +
            '/bin/conda env list | awk \'{ if( !($1=="#") ) print $1 }\'',
        ).split('\n')

    def write_new_md5sum(self):
        """Write new md5sum of ``meta.yaml`` to ``conda-build/meta.md5``."""
        message(text='write md5sum of meta.yaml', color='bold', special='row')
        command = (
            'echo "$(md5sum $PWD/conda-build/meta.yaml)" | '
            'cut -d\' \' -f1 > $PWD/conda-build/meta.md5'
        )
        run_in_bash(cmd=command)
        message(text='updated', color='green', special='end', indent=2)

    def export_environment_definition(self) -> NoReturn:
        """Export projects environment definition to an ``environment.yml``."""
        message(text='Export environment.yml ...', color='bold', special='row')
        run_in_bash(cmd=self.cmds.export.format(**self.cmd_kwargs))
        message(text='Exported', color='green', special='end', indent=2)

    def _remove_backup_environment(self) -> NoReturn:
        """Remove backup environment cloned from original environment."""
        run_in_bash(cmd=self.cmds.clean.format(**self.cmd_kwargs))

    def _restore_environment_from_backup(self, cloned: bool) -> NoReturn:
        """Restore the environment from the cloned backup environment.

        After restore the backup environment is removed.

        Parameters:
            cloned: indicates if the environment already existed and a backup
                was created.

        """
        message(text='Error during creation!', color='red', special='row')
        if self.is_env and cloned:
            message(text='Recreating backup', color='bold', special='row')
            run_in_bash(cmd=self.cmds.restore.format(**self.cmd_kwargs))
            self._remove_backup_environment()
            message(text='Recreated', color='green', special='end', indent=2)
        message(text='Exit', color='red', special='end')

    def _remove_previous_environment(self) -> NoReturn:
        """Remove old version of project environment.

        If the old environment can't be removed, the backup made is removed.
        """
        try:
            message(text='Remove existing env', color='bold', special='row')
            run_in_bash(cmd=self.cmds.remove.format(**self.cmd_kwargs))
            message(text='Removed', color='green', special='end', indent=2)
        except CenvProcessError:
            self._remove_backup_environment()
            message(
                text=(
                    'Could not remove environment because it is '
                    'activated! Please deactivate it first.'
                ),
                color='red',
            )
            exit(1)

    def clone_environment_as_backup(self) -> NoReturn:
        """Clone the existing environment as a backup.

        If the backup already exists, the previous backup is removed, then
        the new one is created by cloning the current project environment.
        """
        backup_name = f'{self.env_name}_backup'
        if backup_name in self.collect_available_envs():
            message(text='Clear old backup', color='bold', special='row')
            self._remove_backup_environment()
            message(text='Cleared', color='green', special='end', indent=2)
        message(text='Create backup', color='bold', special='row')
        run_in_bash(cmd=self.cmds.clone.format(**self.cmd_kwargs))
        message(text='Created', color='green', special='end', indent=2)

    def _handle_existing_environment(self) -> bool:
        """Check if environment already exists and create a backup of it."""
        if self.is_env:
            self.clone_environment_as_backup()
            self._remove_previous_environment()
            return True

        return False

    def create_environment(self, cloned: bool) -> NoReturn:
        """Create the environment for the project.

        Try to create the environment for the project. If the environment
        already existed and a backup was made and any error occure, restore the
        backup environment.
        If everything worked correctly finally remove the backup (if one was
        made).

        Parameters:
            cloned: indicates if the environment already existed and a backup
                was created.

        """
        message(text='Create environment', color='bold', special='row')

        try:
            run_in_bash(cmd=self.cmds.create.format(**self.cmd_kwargs))
        except CenvProcessError:
            self._restore_environment_from_backup(cloned=cloned)
            exit(1)

        if cloned:
            message(text='Clear backup', color='bold', special='row', indent=2)
            run_in_bash(cmd=self.cmds.clean.format(**self.cmd_kwargs))
            message(text='Cleared', color='green', special='end', indent=3)

        message(text='Created', color='green', special='end', indent=2)

    def update(self) -> NoReturn:
        """Create / recreate the conda environment of the current project.

        If the conda environment already exists, clone the environment as a
        backup and then remove original environment. Then create the new
        conda environment. If a backup was created it is
        removed afterwards. If any errors occurs during creation of the new
        environment, recreate the old environment from backup and remove the
        backup afterwards. If activated in the config-file, export the
        environment-definition of the created environment to an
        ``environment.yml`` file. Finally store the md5sum of the meta.yaml for
        the autoupdate feature.
        """
        if self.is_env:
            message(text=f'Updating {self.env_name}', color='cyan')
        else:
            message(text=f'Creating {self.env_name}', color='cyan')

        cloned = self._handle_existing_environment()

        self.create_environment(cloned=cloned)

        if self.export_environment_yml:
            self.export_environment_definition()

        self.write_new_md5sum()

        message(text='Done', color='green', special='end')


def _build_arguments() -> ArgumentParser:
    """Create arguments for the cenv-tool.

    Returns:
        the parsed arguments.

    """
    parser = ArgumentParser(
        description=ARGPARSE_DESCRIPTION,
        epilog='For additional information see http://www.cenv.ouroboros.info',
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        '-v',
        '--version',
        action='store_true',
        default=False,
        help='Show current version of cenv and exit.',
    )
    return parser


def main() -> NoReturn:
    """Collect the required args, initialize and run the Project."""
    parser = _build_arguments()
    options = parser.parse_args()
    if options.version:
        print(__version__)
    else:
        Project(rules=RULES).update()


if __name__ == '__main__':
    main()
