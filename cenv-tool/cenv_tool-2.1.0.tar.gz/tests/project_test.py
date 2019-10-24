# -*- coding: utf-8 -*-
import os
from pathlib import Path

import pytest

from cenv_tool.project import _build_arguments
from cenv_tool.project import Project
from cenv_tool.rules import RULES


def test_project_collect_available_envs():
    """Test if available_envs can be collected."""
    current_path = Path.cwd()
    testfolder = Path('tests/testproject')
    os.chdir(str(testfolder))
    project = Project(rules=RULES)
    os.chdir(str(current_path))
    assert project.collect_available_envs()


@pytest.mark.datafiles('tests/testproject')
def test_project_update(datafiles):
    """Test the project environment creation, update, backup and cleanup."""
    created_env = Path('/shared/conda/envs/cenv_testing_project0001')
    environment_yml = Path(datafiles) / 'conda-build/environment.yml'
    current_folder = Path.cwd()

    # test creation of environment
    os.chdir(datafiles)
    project = Project(rules=RULES)
    assert 'cenv_testing_project0001' not in project.collect_available_envs()

    project.update()
    assert created_env.exists()
    assert 'cenv_testing_project0001' in project.collect_available_envs()


    # test update of environment and the export of the environment.yml
    project = Project(rules=RULES)
    project.export_environment_yml = True
    project.update()
    assert created_env.exists()
    assert 'cenv_testing_project0001' in project.collect_available_envs()


    # test remaining methods for project environment
    project = Project(rules=RULES)
    project._remove_previous_environment()
    project._remove_backup_environment()
    project.create_environment(cloned=False)
    project.export_environment_definition()
    assert environment_yml.exists()


    # clean everything after tests
    environment_yml.unlink()
    project._remove_previous_environment()
    project._remove_backup_environment()
    os.chdir(str(current_folder))


@pytest.mark.datafiles('tests/missing_meta_yaml')
def test_no_meta_yaml(datafiles):
    """Test if exit if no meta.yaml is found."""
    current_folder = Path.cwd()
    os.chdir(datafiles)
    with pytest.raises(SystemExit):
        project = Project(rules=RULES)
    os.chdir(str(current_folder))


def test_build_arguments():
    """Test if the option --version is parsable."""
    parser = _build_arguments()
    options = parser.parse_args(['--v'])
    assert options.version
