#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `publishing_boy` package."""
import os

from click.testing import CliRunner
from publishing_boy.cli import main

TEST_FILE = 'test.md'
TEST_FOLDER = 'test_folder'
TEST_OUTPUT_FILE = 'test_output/test.md'


def test_command_line_folders():
    """Go to cookiecutter download folder, and
    extract the contents with cli testing.

    Test different types of input folders
    """
    from tests.fixtures import ContentFile, get_test_storage, filename, content

    temp_dir, storage = get_test_storage()

    input_folder = os.path.join(temp_dir, 'input')
    output_folder = os.path.join(temp_dir, 'output')

    os.makedirs(input_folder)

    filepath = os.path.join(input_folder, filename)
    result_filename = os.path.join(output_folder, filename)

    storage.save(filepath, ContentFile(content))

    assert storage.exists(result_filename) is False

    runner = CliRunner()
    result = runner.invoke(main, [input_folder, output_folder])

    assert result.exit_code == 0
    assert storage.exists(output_folder)
    assert storage.exists(result_filename)
