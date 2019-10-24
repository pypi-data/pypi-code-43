# -*- coding: utf-8 -*-
"""Contain utils required by cenv-tool."""
import os
from pathlib import Path
from subprocess import CalledProcessError
from subprocess import check_output
from subprocess import STDOUT
from typing import List
from typing import NoReturn

import jinja2
import six
import yaml
from marshmallow import ValidationError

from cenv_tool.schemata import SMetaYaml

CYAN = '\033[1;36m'
GREEN = '\033[1;32m'
RED = '\033[1;91m'
NCOLOR = '\033[0m'
BOLD = '\033[1;37m'


class CenvProcessError(Exception):
    """Represent a process error during cenv execution."""


def message(
    *, text: str, color: str, special: str = None, indent: int = 1
) -> NoReturn:
    """Print passed ``text`` in the passed ``color`` on terminal.

    Parameters:
        text: the text to print colored on terminal.
        color: the color of the text to print.
        special: special kind of message to print. Available are ``'row'`` and
            ``'end'``.
        indent: the indent to use for the text.

    """
    color_mapping = {
        'red': RED,
        'green': GREEN,
        'cyan': CYAN,
        'bold': BOLD,
    }
    if indent == 1:
        indent_prefix = '   ' * indent
    else:
        indent_prefix = '   ' + '│   ' * (indent - 1)
    special_mapping = {
        'row': f'{indent_prefix}├── ',
        'end': f'{indent_prefix}└── ',
    }

    if special:
        prefix = special_mapping[special]
    else:
        prefix = ''
    print(f'{prefix}{color_mapping[color]}{text}{NCOLOR}')


def run_in_bash(cmd: str) -> str:
    """Run passed ``cmd`` inside bash using :func:`subprocess.check_output`.

    Parameters:
        cmd: the command to execute.

    Returns:
        the output of the ran command.

    """
    try:
        result = check_output([cmd], shell=True, stderr=STDOUT)
    except CalledProcessError as err:
        error_message = err.output.decode('utf8').split('\n')
        message(text='the following error occured:', color='red')
        for line in error_message:
            message(text=line, color='bold')
        raise CenvProcessError(str(err.output))
    return result.strip().decode('ascii')


class _NullUndefined(jinja2.Undefined):
    """Handle jinja2-variables with undefined content of ``meta.yaml.``"""

    def __unicode__(self):
        """Replace unicode dunder of this class."""
        return six.text_type(self._undefined_name)

    def __getattr__(self, attribute_name: str):
        """Replace getattr dunder of this class."""
        return six.text_type(f'{self}.{attribute_name}')

    def __getitem__(self, attribute_name: str):
        """Replace getitem dunder of this class."""
        return f'{self}["{attribute_name}"]'


class _StrDict(dict):
    """Handle dictionaries for jinja2-variables of ``meta.yaml``."""

    def __getitem__(self, key: str, default: str = '') -> str:
        """Replace getitem dunder of this class."""
        return self[key] if key in self else default


def extract_dependencies_from_meta_yaml(meta_yaml_content: dict) -> List[str]:
    """
    Extract the dependencies defined in the requirements-run-section.

    If additional dev-requirements are defined in the
    extra-dev_requirements-section, these dependencies are added to the other
    dependencies.

    Parameters:
        meta_yaml_content: the content from a ``meta.yaml`` as a dict.

    Returns:
        the collected dependencies.

    """
    # extract the dependencies defined the the requirements-run-section
    dependencies = meta_yaml_content['requirements']['run']

    # remove the python version definition. The version will be extracted
    # from the extra-python section
    dependencies = list(
        filter(
            lambda x: x.split(' ')[0] != 'python',
            dependencies
        )
    )

    if meta_yaml_content['requirements'].get('run_constrained'):
        dependencies.extend(
            meta_yaml_content['requirements']['run_constrained']
        )

    if meta_yaml_content['extra'].get('dev_requirements'):
        dependencies.extend(meta_yaml_content['extra']['dev_requirements'])

    # append the python version to use in the conda environment
    dependencies.append(f'python {meta_yaml_content["extra"]["python"]}')
    return dependencies


def read_meta_yaml(path: Path) -> dict:
    """Read the meta.yaml file.

    The file is read from relative path ``conda-build/meta.yaml`` inside
    the current path, validate the ``meta.yaml`` using the marshmallow-schema,
    :class:`SMetaYaml`, extract the project-settings.

    Parameters:
        path: the current working directory.

    Returns:
        the ``meta.yaml`` content as a dict.

    """
    # load the meta.yaml-content
    myaml_content = (path / 'conda-build/meta.yaml').open().read()
    jinja2_env = jinja2.Environment(undefined=_NullUndefined)
    jinja2_loaded_myaml = jinja2_env.from_string(myaml_content)
    render_kwargs = {
        'os': os,
        'environ': _StrDict(),
        'load_setup_py_data': _StrDict,
    }
    rendered_myaml = jinja2_loaded_myaml.render(**render_kwargs)
    loaded_myaml = yaml.safe_load(rendered_myaml)

    # validate the content of loaded meta.yaml
    try:
        dumped = SMetaYaml(strict=True).dumps(loaded_myaml).data
        meta_yaml_content = SMetaYaml(strict=True).loads(dumped).data
    except ValidationError as err:
        message(text='meta.yaml file is not valid!', color='red')
        message(text=f'ValidationError in {err.args[0]}', color='red')
        raise

    # return combined collected project-settings
    return meta_yaml_content


def read_config():
    """Read the config file for cenv from the users-home path if it exists.

    If there is no user-config-file the default one is used.

    Returns:
        the content of the read config file.

    """
    user_config_path = Path.home() / '.config/cenv/cenv.yml'
    default_config_path = Path(__file__).parent / 'cenv.yml'

    # Collect settings from config file .cenv.yml
    main_config = yaml.safe_load(default_config_path.open().read())

    # if a user-config-file exists, read the content and update the main-config
    if user_config_path.exists():
        user_config = yaml.safe_load(user_config_path.open().read())
        main_config.update(user_config)

    return main_config
