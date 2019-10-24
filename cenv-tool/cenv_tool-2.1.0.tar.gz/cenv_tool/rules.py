# -*- coding: utf-8 -*-
"""Rules-definitions required by cenv."""
import attr

EXAMPLE_META_YAML = """
        {% set data = load_setup_py_data() %}

        package:
            name: "example_package"
            version: {{ data.get("version") }}

        source:
            path: ..

        build:
            build: {{ environ.get('GIT_DESCRIBE_NUMBER', 0) }}
            preserve_egg_dir: True
            script: python -m pip install --no-deps --ignore-installed .

        requirements:
            build:
              - python 3.6.8
              - pip
              - setuptools
            run:
              - python 3.6.8
              - attrs >=18.2
              - marshmallow >=3.0.0rc1*

        test:
            imports:
                - example_package

        extra:
            env_name: example
            dev_requirements:
                - ipython >=7.2.0
                - pylint >=2.3.1
"""

ARGPARSE_DESCRIPTION = (
    """
    Create / update conda environments from meta.yaml definition.
    Due to the redundant dependency information inside the
    meta.yaml (required to create conda-package)
    and the environment.yml (definition for conda environment),
    cenv (short for `conda-env-manager`) was created to make the
    meta.yaml the only relevant file for creation and update of
    conda environments.
    The name of the conda-environment to create / update is defined
    in the section "extra" and the variable "env_name" inside the
    meta.yaml.
    Dependencies and their versions are extracted from the
    "requirements-run"-section of the meta.yaml.
    Dependencies required during development are defined in the
    "dev_requirements"-section.

    Steps run by cenv:
      * Cloning existing environment as backup if already exists
      * Removing existing environment if already exists
      * Creating environment from definition in meta.yaml
      * Removing backup environment if everything worked as expected
      * Exporting env to environment.yml (only if activated in config)'


    IMPORTANT:
        if you do not use the functionalities "autoactivate" and
        "autoupdate" from cenv.sh you have to deactivate the
        environment before running cenv.


    An example for a valid meta.yaml:
    """ + EXAMPLE_META_YAML
)


@attr.s(slots=True, auto_attribs=True)
class CondaCmdFormats:
    """Contain the formats for the conda commands to use inside cenv.

    Attributes:
        remove: command to remove a conda environment.
        export: command to use to export a conda environment to an
            environment definition file (environment.yml).
        create: command to use for conda environment creation.
        clone: command to use to clone a conda environment.
        restore: command to use to recreate a conda environment from backup
            conda environment (clone).
        clean: command to use to remove the backup conda environment.
    """

    remove: str = attr.ib(default='{conda} remove -n {name} --all -y')
    export: str = attr.ib(
        default='{conda} env export -n {name} > conda-build/environment.yml'
    )
    create: str = attr.ib(default='{conda} create -n {name} {pkgs} -y')
    clone: str = attr.ib(
        default='{conda} create -n {name}_backup --clone {name} -y'
    )
    restore: str = attr.ib(
        default='{conda} create -n {name} --clone {name}_backup -y'
    )
    clean: str = attr.ib(default='{conda} remove -n {name}_backup --all -y')

    def conda_bin(self, conda_folder):
        """Combine the path of conda-folder with subpath of conda-bin.

        Returns:
            the path to the conda-executable

        """
        return (conda_folder / 'bin/conda').absolute()


@attr.s(slots=True)
class Rules:
    """Contain the rules required by cenv-tool."""

    conda_cmds: CondaCmdFormats = CondaCmdFormats()
    git_folder: str = '.git'


RULES = Rules()
