# -*- coding: utf-8 -*-
import sys

from story.cli import cli


def test_cli_as_module(spawn_cli_subprocess):
    # We don't need space-indents from docstrings
    output = str(cli.__doc__).replace('  ', ' ').strip()
    exit_code, stdout, stderr = spawn_cli_subprocess()

    assert exit_code == 0
    assert output in stdout
    assert stderr == ''
