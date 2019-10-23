# pylint: disable=missing-docstring

import os

import pytest
import yaml

TESTS_DIR = os.path.dirname(os.path.relpath(__file__))
TESTS_DATA_DIR = os.path.join(TESTS_DIR, "data")
CONFIG_TEMPLATE = os.path.join(TESTS_DIR, os.pardir, "polarion_tools.yaml.template")


@pytest.fixture(scope="session")
def source_file():
    return os.path.join(TESTS_DATA_DIR, "docstrings_func.py")


@pytest.fixture(scope="session")
def source_file_merge():
    return os.path.join(TESTS_DATA_DIR, "docstrings_merge.py")


@pytest.fixture(scope="session")
def config():
    with open(CONFIG_TEMPLATE, encoding="utf-8") as config_file:
        config_loaded = yaml.safe_load(config_file)
    return config_loaded
