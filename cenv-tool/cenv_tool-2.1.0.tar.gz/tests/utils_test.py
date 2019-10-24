# -*- coding: utf-8 -*-
"""Test the utils module of cenv."""
from pathlib import Path

import pytest
from marshmallow import ValidationError

from cenv_tool.utils import CenvProcessError
from cenv_tool.utils import extract_dependencies_from_meta_yaml
from cenv_tool.utils import read_meta_yaml
from cenv_tool.utils import run_in_bash
from cenv_tool.utils import _StrDict


@pytest.mark.parametrize(
    'meta_yaml_path, expected_meta_yaml_content',
    [
        (
            Path('tests/testproject'),
            {
                'requirements': {
                    'build': ['python', 'pip', 'setuptools'],
                    'run': [
                        'python',
                        'attrs >=19',
                        'jinja2 >=2.10',
                        'six >=1.12.0',
                        'yaml >=0.1.7',
                    ],
                    'run_constrained': ['pandas >=0.23']
                },
                'extra': {
                    'dev_requirements': ['pylint >=2.2.2'],
                    'python': '3.7.3',
                    'env_name': 'cenv_testing_project0001',
                },
                'source': {
                    'path': '..',
                },
                'test': {
                    'commands': [
                        'cenv_testing_project0001 --help',
                        'cenv_testing_project0001 -v',
                    ],
                    'imports': ['cenv_testing_project0001'],
                },
                'build': {
                    'build': '0',
                    'preserve_egg_dir': 'True',
                    'script':
                    'python -m pip install --no-deps --ignore-installed .',
                    'entry_points':
                    ['testproject = testproject.testproject:main'],
                },
                'package': {
                    'version': 'None',
                    'name': 'cenv_testing_project0001',
                },
            },
        ),
    ],
)
def test_read_meta_yaml(
    meta_yaml_path,
    expected_meta_yaml_content,
):
    """Test if the read_meta_yaml function works as expected."""
    meta_yaml_content = read_meta_yaml(path=meta_yaml_path)
    assert meta_yaml_content == expected_meta_yaml_content


@pytest.mark.parametrize(
    'meta_yaml_path, expected_dependencies',
    [
        (
            Path('tests/testproject'),
            [
                'python 3.7.3',
                'attrs >=19',
                'jinja2 >=2.10',
                'six >=1.12.0',
                'yaml >=0.1.7',
                'pylint >=2.2.2',
                'pandas >=0.23'
            ],
        ),
    ],
)
def test_extract_dependencies_from_meta_yaml(
    meta_yaml_path,
    expected_dependencies,
):
    """Test if the read_meta_yaml function works as expected."""
    meta_yaml_content = read_meta_yaml(path=meta_yaml_path)
    dependencies = extract_dependencies_from_meta_yaml(meta_yaml_content)
    assert list(sorted(expected_dependencies)) == list(sorted(dependencies))



@pytest.mark.parametrize('meta_yaml_path', [Path('tests/invalid_testproject')])
def test_read_meta_yaml_fails(meta_yaml_path):
    """Test if read_meta_yaml function fails on invalid meta.yaml."""
    with pytest.raises(ValidationError):
        read_meta_yaml(path=meta_yaml_path)


def test_run_in_bash():
    """Test if run_in_bash works as expected."""
    cmd_result = run_in_bash(cmd='ls tests/testproject/conda-build')
    assert cmd_result == 'meta.yaml'


def test_run_in_bash_fails():
    """Test if run_in_bash works as expected."""
    with pytest.raises(CenvProcessError):
        run_in_bash(cmd='ls-a tests/testproject/conda-build')


def test_strdict():
    example_dict = _StrDict({
        'a': 1,
        'b': {
            'c': 'test'
        },
        'd': ''
    })
    assert example_dict.get('a') == 1
    assert example_dict.get('b') == {'c': 'test'}
    assert not example_dict.get('d')
    assert not example_dict.get('e')
