"""Unit tests for the bazel_workspaces_python.sources module."""

import os
import pathlib

import bazel_workspaces_python
from bazel_workspaces_python import sources


def test_get_module_sources():
    """Test for the get_module_sources function."""
    project_dir = pathlib.Path(bazel_workspaces_python.__path__[0]).parent
    tests = (
        (
            "setuptools", [os.path.join(project_dir, ".tox/py36/lib/python3.6/"
                                        "site-packages/setuptools/**/*.py")],
        ), (
            "pip", [os.path.join(project_dir, ".tox/py36/lib/python3.6/site-"
                                 "packages/pip/**/*.py")],
        ),
    )

    for name, expected in tests:
        module_sources = sources.get_module_sources(name)
        assert module_sources == expected
