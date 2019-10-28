"""Test cli_profile module."""


import os

import pytest
import click

from ptvpy import _profile, _cli_profile


def test_help_option(runner):
    """Test "-h" and "--help" option for all view commands."""
    commands = ["", "create", "check", "edit", "diff"]
    for cmd in commands:
        result = runner(f"profile {cmd} -h")
        assert result.exit_code == 0
        result = runner(f"profile {cmd} --help")
        assert result.exit_code == 0


def test_create_command(runner, tmp_path):
    """Test behavior of the `ptvpy profile create` command."""
    os.chdir(tmp_path)
    # Create dummy image file
    with open("image_0.tif", "x") as stream:
        stream.write("dummy file")

    result = runner("profile create")
    assert result.exit_code == 0
    assert "Created" in result.output
    assert "Warning" not in result.output
    assert _profile.Profile("ptvpy.toml").is_valid

    # Compare with template
    with open(_profile.template_path()) as stream:
        template = stream.read()
    with open("ptvpy.toml") as stream:
        new_file = stream.read()
    assert new_file == template

    # Calling a second time should fail, as file already exists
    result = runner("profile create")
    assert result.exit_code == 1
    assert isinstance(result.exception, FileExistsError)
    assert "already exists" in result.exception.args[0]

    # Create second profile with mismatching pattern
    result = runner("profile create --data-files '*.jpg' --path 'profile_2.ptvpy.toml'")
    assert result.exit_code == 0
    assert "Created" in result.output
    assert "Warning" in result.output
    assert "data_files: must match" in result.output
    assert not _profile.Profile("profile_2.ptvpy.toml").is_valid


def test_edit_command(runner, tmp_path, monkeypatch):
    os.chdir(tmp_path)
    _profile.create_profile_file("ptvpy.toml", data_files="foo")

    # We don't actually want to open the file inside an editor, so we temporarily
    # replace the appropriate function and check its input once called
    mock_ptr = {}

    def mocked_launch(url, wait=False, locate=False):
        mock_ptr["url"] = url
        assert wait is False
        assert locate is False

    monkeypatch.setattr(click, "launch", mocked_launch)

    result = runner("profile edit")
    assert result.exit_code == 0
    assert "Using profile: 'ptvpy.toml'\n" == result.stdout
    assert mock_ptr["url"] == "ptvpy.toml"


class Test_check_command:
    """Test behavior of the `ptvpy profile check` command."""

    def test_valid(self, runner, fresh_project):
        """Directory with single valid profile."""
        expected = (
            "Checking files matching '*ptvpy*.toml':\n\n'ptvpy.toml' is a "
            "valid profile\n\n"
        )

        result = runner("profile check")
        assert result.exit_code == 0
        assert result.output == expected

        result = runner("profile check --pattern '*ptvpy*.toml'")
        assert result.exit_code == 0
        assert result.output == expected

    def test_not_matching(self, runner, tmp_path):
        """Directory with no matching files."""
        os.chdir(tmp_path)
        with open("unrelated.toml", "x") as stream:
            stream.write("unrelated: true")
        expected = "Checking files matching '{pattern}':\n\nno matching files\n\n"

        result = runner("profile check")
        assert result.exit_code == 0
        assert result.output == expected.format(pattern="*ptvpy*.toml")

        os.mkdir("subdir")
        result = runner("profile check --pattern 'subdir/*'")
        assert result.exit_code == 0
        assert result.output == expected.format(pattern=f"subdir{os.sep}*")

    def test_invalid(self, runner, tmp_path):
        """Directory with matching but invalid profiles."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        for current_dir in [subdir, tmp_path]:
            os.chdir(current_dir)
            _profile.create_profile_file("1_invalid.ptvpy.toml", "invalid.tiff")
            with open("2_empty.ptvpy.toml", "x"):
                pass  # Create empty file
            with open("3_invalid_toml.ptvpy.toml", "x") as stream:
                stream.write("src_files: 1: 2")  # Create file with invalid toml
            with open("4_unrelated.toml", "x") as stream:
                stream.write("src_files: '*.tiff'")  # Shouldn't be checked

        expected = """Checking files matching '{directory}*ptvpy*.toml':

'{directory}1_invalid.ptvpy.toml' is not a valid profile:
    general.data_files: must match at least once and never a directory

'{directory}2_empty.ptvpy.toml' is not a valid profile:
    general: required field
    step_diff: required field
    step_link: required field
    step_locate: required field

'{directory}3_invalid_toml.ptvpy.toml' is not a valid profile:
    Found invalid character in key name: ':'. Try quoting the key name. (line 1 column 10 char 9)

"""  # noqa: E501

        result = runner("profile check")
        assert result.exit_code == 0
        assert result.output == expected.format(directory="")

        result = runner("profile check --pattern 'subdir/*ptvpy*.toml'")
        assert result.exit_code == 0
        assert result.output == expected.format(directory="subdir" + os.sep)


class Test_diff_command:
    def test_output(self, runner, tmp_path):
        """Test formatting and coloring."""
        os.chdir(tmp_path)
        template = "# This is a test\nfile_name = {value}\n\n# Another comment\n"
        with open("a.toml", "x") as stream:
            stream.write(template.format(value="a.toml"))
        with open("b.toml", "x") as stream:
            stream.write(template.format(value="b.toml"))

        result = runner("profile diff a.toml b.toml", color=True)
        assert result.exit_code == 0
        expected_stdout = """[31m--- a.toml
[0m[32m+++ b.toml
[0m[35m@@ -1,4 +1,4 @@
[0m # This is a test
[0m[31m-file_name = a.toml
[0m[32m+file_name = b.toml
[0m 
[0m # Another comment
[0m
"""  # noqa: W291, the trailing whitespace is actually present
        assert result.stdout == expected_stdout

    def test_no_argument(self, runner, tmp_path):
        os.chdir(tmp_path)
        _profile.create_profile_file("ptvpy.toml", data_files="foo")
        result = runner("profile diff")
        assert result.exit_code == 0
        assert f"--- {_profile.template_path()}\n" in result.stdout
        assert f"\n+++ ptvpy.toml\n" in result.stdout

    def test_one_argument(self, runner, tmp_path):
        os.chdir(tmp_path)
        _profile.create_profile_file("ptvpy.toml", data_files="foo")
        _profile.create_profile_file("other.toml", data_files="*.jpg")
        result = runner("profile diff other.toml")
        assert result.exit_code == 0
        assert f"--- {_profile.template_path()}\n" in result.stdout
        assert f"\n+++ other.toml\n" in result.stdout

    def test_two_arguments(self, runner, tmp_path):
        os.chdir(tmp_path)
        _profile.create_profile_file("ptvpy.toml", data_files="foo")
        _profile.create_profile_file("other.toml", data_files="bar")
        result = runner("profile diff ptvpy.toml other.toml")
        assert result.exit_code == 0
        assert f"--- ptvpy.toml\n" in result.stdout
        assert f"\n+++ other.toml\n" in result.stdout

    def test_identical(self, runner, tmp_path):
        os.chdir(tmp_path)
        _profile.create_profile_file("a.toml", data_files="foo")
        _profile.create_profile_file("b.toml", data_files="foo")
        result = runner("profile diff a.toml b.toml")
        assert result.exit_code == 0
        assert '"a.toml" and "b.toml" are identical\n' == result.stdout

    def test_to_many(self, capsys, tmp_path):
        os.chdir(tmp_path)
        _profile.create_profile_file("a.toml", data_files="foo")
        _profile.create_profile_file("b.toml", data_files="bar")
        _profile.create_profile_file("c.toml", data_files="baz")
        # Use command directly instead of invocation via a runner because the raised
        # exception type is caught by click turned into a SystemExit
        msg = "to many arguments: expected 0-2, got 3"
        with pytest.raises(click.BadArgumentUsage, match=msg):
            _cli_profile.diff_command(
                ["a.toml", "b.toml", "c.toml"], standalone_mode=False
            )
        stdout, stderr = capsys.readouterr()
        assert "" == stdout == stderr
