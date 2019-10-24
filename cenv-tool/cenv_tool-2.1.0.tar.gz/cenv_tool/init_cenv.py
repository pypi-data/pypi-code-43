# -*- coding: utf-8 -*-
"""Install config and cenv.sh."""
from pathlib import Path
from typing import NoReturn

from cenv_tool.utils import message

CONFIG_PATH = Path.home() / '.config/cenv'
AUTOENV_SCRIPT_PATH = CONFIG_PATH / 'cenv.sh'
AUTOENV_SCRIPT_SOURCE_PATH = Path(__file__).with_name('cenv.sh')
CONFIG_FILE = CONFIG_PATH / 'cenv.yml'
CONFIG_FILE_SOURCE = Path(__file__).with_name('cenv.yml')
ZSHRC = Path.home() / '.zshrc'
BASHRC = Path.home() / '.bashrc'

RC_CONTENT = """
# ======================================================================>>>>>>>
# AUTOMATICALLY ADDED BY CENV TO ENABLE AUTOUPDATE AND AUTOACTIVATE

# load the cenv shell functions
source $HOME/.config/cenv/cenv.sh

# 0 means deactivated, 1 activated
# disable autoactivate
export AUTOACTIVATE=0
# disable autoupdate
export AUTOUPDATE=0

# enable the autoactivation of conda-environments
precmd() { autoactivate_env; }
# <-----
# <<<<<<<======================================================================
"""


def initialize_cenv(
    config_path: Path,
    autoenv_script_path: Path,
    autoenv_script_source_path: Path,
    config_file: Path,
    config_file_source: Path,
    zshrc: Path,
    bashrc: Path,
) -> NoReturn:
    """
    Install user-config and cenv.sh for autoactivate and autoupdate.

    Parameters:
        config_path: the path for cenv config-stuff.
        autoenv_script_path: the path to install the cenv.sh script to.
        autoenv_script_source_path: the path where to get the cenv.sh script from
        config_file: the path to install the user-config into.
        config_file_source: the path where to get the config file from.
        zshrc: the path to the users .zshrc
        bashrc: the path to the users .bashrc

    """
    if not config_path.exists():
        message(text='creating cenv-config folder', color='cyan')
        config_path.mkdir(parents=True)
        message(text='created cenv-config folder', color='green')
    else:
        message(text='cenv-config folder already exists', color='green')

    if not autoenv_script_path.exists():
        message(
            text=(
                'copying script for autoactivation and autoupdate to '
                'config-folder'
            ),
            color='cyan',
        )
        autoenv_script_path.write_text(autoenv_script_source_path.read_text())
        message(
            text='copied script for autoactivateion and autoupdate',
            color='green',
        )
    else:
        message(
            text='script for autoactivation and autupdate already copied',
            color='green',
        )

    if not config_file.exists():
        message(
            text='copying config-file to cenv-config-folder ...',
            color='cyan',
        )
        config_file.write_text(config_file_source.read_text())
        message(text='copied config-file', color='green')
    else:
        message(text='config-file already exists', color='green')

    for shell_config in (zshrc, bashrc):
        if shell_config.exists():
            if RC_CONTENT not in shell_config.read_text():
                message(
                    text=f'initilized cenv in {shell_config}',
                    color='green',
                )
                with open(shell_config, 'a') as opened_shell_config:
                    opened_shell_config.write(RC_CONTENT)
            else:
                message(
                    text=f'cenv already initialized in {shell_config}',
                    color='green',
                )


def main():
    """Call the initialization function to install config and cenv.sh."""
    initialize_cenv(
        config_path=CONFIG_PATH,
        autoenv_script_path=AUTOENV_SCRIPT_PATH,
        autoenv_script_source_path=AUTOENV_SCRIPT_SOURCE_PATH,
        config_file=CONFIG_FILE,
        config_file_source=CONFIG_FILE_SOURCE,
        zshrc=ZSHRC,
        bashrc=BASHRC,
    )


if __name__ == '__main__':
    main()
