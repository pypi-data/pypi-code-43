"""Test _cli_utils module."""


import os
import re
import time
from types import ModuleType

import click
import pytest
from click.testing import CliRunner

from ptvpy._cli_utils import (
    LazyImport,
    CliTimer,
    AddProfileDetection,
    DetectionError,
    ValidationError,
)
from ptvpy._profile import Profile, create_profile_file


class Test_LazyImport:
    @pytest.mark.parametrize(
        "name, package",
        [
            ("math", None),
            ("numpy.testing", None),
            ("signal", "scipy.fftpack"),
            ("..conftest", __name__),
        ],
    )
    def test_working(self, name, package):
        lazy = LazyImport(name, package)
        lazy_dict = object.__getattribute__(lazy, "__dict__")
        assert name in repr(lazy)
        # Module is not imported yet
        assert "module" not in lazy_dict
        # Attribute access should import module
        _ = lazy.__name__
        assert "module" in lazy_dict
        assert isinstance(lazy_dict["module"], ModuleType)

    @pytest.mark.parametrize(
        "name, package, error_type",
        [
            ("mathh", None, ModuleNotFoundError),
            ("numpy.testingg", None, ModuleNotFoundError),
            ("signall", "scipy.fftpack", ModuleNotFoundError),
            ("..conftestt", __file__, ModuleNotFoundError),
            ("", None, ValueError),
            (None, None, ModuleNotFoundError),
        ],
    )
    def test_invalid(self, name, package, error_type):
        lazy = LazyImport(name, package)
        with pytest.raises(error_type):
            _ = lazy.__name__

    def test_setattr(self):
        lazy = LazyImport("math")
        assert lazy.pi
        with pytest.raises(AttributeError, match="not supported"):
            lazy.pi = 3

    def test_get(self):
        import math

        with pytest.raises(TypeError, match="must be of type"):
            LazyImport.get(math, "__name__")
        lazy = LazyImport("math")
        assert LazyImport.get(lazy, "name") == "math"
        assert LazyImport.get(lazy, "package") is None
        with pytest.raises(AttributeError):
            LazyImport.get(lazy, "module")
        assert lazy.__name__ == "math"
        assert LazyImport.get(lazy, "module") is math

    def test_imported(self):
        with pytest.raises(TypeError, match="must be of type"):
            LazyImport.is_imported(pytest)
        lazy = LazyImport("math")
        assert LazyImport.is_imported(lazy) is False
        assert lazy.__name__ == "math"
        assert LazyImport.is_imported(lazy) is True


class Test_CliTimer:

    # Matches "counter/total (percentage)"
    re_progress = r"\d+/\d+ \(1?\d?\d\.\d%\)"
    # Matches time delta in exact formatting
    re_exact = r"(?:\d\.\d\d s|\d?\d\.\d s|\d?\d min \d\d s|\d+ h \d\d min \d\d s)"
    # Matches time delta in rounded formatting
    re_rounded = r"(?:\d?\d s|\d?\d min \d\d s|\d\d min|\d+ h \d\d min)"

    @pytest.mark.parametrize(
        "seconds, expected",
        [
            (0, "0.00 s"),
            (0.998, "1.00 s"),
            (1.060, "1.1 s"),
            (59.999, "60.0 s"),
            (60.1, "1 min 00 s"),
            (122, "2 min 02 s"),
            (3599.8, "1 h 00 min 00 s"),
            (3600, "1 h 00 min 00 s"),
            (8888, "2 h 28 min 08 s"),
        ],
    )
    def test_format_exact(self, seconds, expected):
        exact = CliTimer.format_exact(seconds)
        assert exact == expected
        assert re.fullmatch(self.re_exact, exact)

    @pytest.mark.parametrize(
        "seconds, expected",
        [
            (0, "0 s"),
            (0.998, "1 s"),
            (55.96, "56 s"),
            (59.999, "1 min 00 s"),
            (74.5, "1 min 10 s"),
            (122, "2 min 00 s"),
            (1022, "17 min"),
            (3599.8, "1 h 00 min"),
            (3600, "1 h 00 min"),
            (8888, "2 h 30 min"),
        ],
    )
    def test_format_rounded(self, seconds, expected):
        rounded = CliTimer.format_rounded(seconds)
        assert rounded == expected
        assert re.fullmatch(self.re_rounded, rounded)

    def test_repeated_usage(self):
        timer = CliTimer("test")
        with timer:
            pass
        with pytest.raises(RuntimeError, match="already started"):
            with timer:
                pass
        with pytest.raises(RuntimeError, match="already stopped"):
            timer._stop()

    @pytest.mark.parametrize("argument", [None, False])
    @pytest.mark.parametrize("total", [None, 20])
    def test_static(self, capsys, argument, total):
        timer = CliTimer("not animated", total=total, animated=argument)
        with timer:
            if total is not None:
                for _ in range(total):
                    timer.update()
            time.sleep(0.1)
        stdout, stderr = capsys.readouterr()
        assert re.fullmatch(rf"not animated: \.{{3}} {self.re_exact} \| done\n", stdout)
        assert not stderr

        timer = CliTimer("not animated", total=total, animated=argument)
        try:
            with timer:
                if total is not None:
                    for _ in range(total // 2):
                        timer.update()
                time.sleep(0.1)
                raise RuntimeError()
        except RuntimeError:
            pass
        stdout, stderr = capsys.readouterr()
        assert "not animated: ... " == stdout
        assert re.fullmatch(rf"{self.re_exact} \| failed\n", stderr)

    def test_animated_total(self, capsys):
        total = 10
        # Regex to match a single status update string
        re_status = (
            rf"{self.re_progress}, {self.re_exact} (?:\(\+ {self.re_rounded}\))?"
        )

        timer = CliTimer("animated", total=total, animated=True)
        with timer:
            for _ in range(total - 1):
                time.sleep(0.01)
                timer.update()
            time.sleep(0.3)  # wait longer than update interval
            timer.update()
        stdout, stderr = capsys.readouterr()
        progress, final = stdout.split("\r")
        assert re.fullmatch(rf"animated: (?:{re_status} *[\b]+)+", progress)
        assert f"{total}/{total}" in final
        assert re.fullmatch(rf"animated: {re_status} +\| done\n", final)

        timer = CliTimer("animated", total=total, animated=True)
        try:
            with timer:
                for i in range(total // 2):
                    time.sleep(0.05)
                    timer.update()
                raise RuntimeError()
        except RuntimeError:
            pass
        stdout, stderr = capsys.readouterr()
        progress, final = stdout.split("\r")
        assert re.fullmatch(rf"animated: (?:{re_status} *[\b]+)+", progress)
        assert final == "animated: "
        assert f"{i + 1}/{total}" in stderr
        assert re.fullmatch(rf"{re_status} +\| failed\n", stderr)

    def test_animated_unkown(self, capsys):
        total = 20
        timer = CliTimer("animated", animated=True)
        with timer:
            for _ in range(total):
                time.sleep(0.05)
                timer.update()
        stdout, stderr = capsys.readouterr()
        progress, final = stdout.split("\r")
        assert re.match(rf"animated: (?:{self.re_exact} *[\b]+)+", progress)
        assert re.match(rf"animated: {self.re_exact} +\| done\n", final)

        timer = CliTimer("animated", animated=True)
        try:
            with timer:
                for i in range(total // 2):
                    time.sleep(0.05)
                    timer.update()
                raise RuntimeError()
        except RuntimeError:
            pass
        stdout, stderr = capsys.readouterr()
        progress, final = stdout.split("\r")
        assert re.match(rf"animated: (?:{self.re_exact} *[\b]+)+", progress)
        assert final == "animated: "
        assert re.match(rf"{self.re_exact} +\| failed\n", stderr)

    def test_interrupt(self, capsys):
        timer = CliTimer("animated", animated=True)
        try:
            with timer:
                timer.update()
                raise KeyboardInterrupt()
        except KeyboardInterrupt:
            pass
        stout, stderr = capsys.readouterr()
        assert "interrupted" in stderr

    def test_exception(self, capsys):
        timer = CliTimer("animated", animated=True)
        try:
            with timer:
                timer.update()
                raise RuntimeError()
        except RuntimeError:
            pass
        stout, stderr = capsys.readouterr()
        assert "failed" in stderr


class Test_AddProfileDetection:
    def test_wrong_usage(self):
        with pytest.raises(TypeError, match="'validation' must be of type bool"):

            @click.command()
            @AddProfileDetection
            def decorated(profile):
                pass

    def test_help(self):
        @click.command()
        @AddProfileDetection()
        def cmd(profile):
            return profile

        runner = CliRunner()
        result = runner.invoke(cmd, args=["--help"])
        assert result.exit_code == 0
        assert "--profile" in result.output
        assert "--no-validation" in result.output

    def test_working(self, fresh_project):
        """Check behavior for expected normal situation."""

        @click.command()
        @AddProfileDetection()
        def cmd(profile):
            return profile

        profile = cmd([], standalone_mode=False)
        assert isinstance(profile, Profile)
        assert profile.is_valid
        assert fresh_project == profile.path.resolve().parent

    def test_empty(self, tmp_path):
        os.chdir(tmp_path)

        @click.command()
        @AddProfileDetection()
        def cmd(profile):
            return profile

        error_msg = "no file matching '*ptvpy*.toml'"
        error_hint = (
            "Explicitly specify a file to use with the option '--profile FILE' or see "
            "'ptvpy profile create -h' for help on creating one."
        )
        with pytest.raises(DetectionError) as exc_info:
            cmd([], standalone_mode=False)
        assert exc_info.value.message == error_msg
        assert exc_info.value.hint == error_hint

    def test_ambiguous(self, fresh_project):
        """Check behavior if multiple candidates are detected."""
        create_profile_file("valid.ptvpy.toml", data_files="*.tif*")
        create_profile_file("invalid.ptvpy.toml", data_files="*.png")

        @click.command()
        @AddProfileDetection()
        def cmd(profile):
            return profile

        with pytest.raises(DetectionError) as exc_info:
            cmd([], standalone_mode=False)
        assert (
            "found more than one file matching '*ptvpy*.toml'" in exc_info.value.message
        )
        assert (
            "Specify which file to use with the '--profile FILE' option:\n"
            "    invalid.ptvpy.toml\n    ptvpy.toml\n    valid.ptvpy.toml"
            in exc_info.value.hint
        )

    def test_remember(self, fresh_project, capsys):
        """Check behavior with remember=True."""
        _add_profile_detection = AddProfileDetection(remember=True)

        @click.command()
        @_add_profile_detection
        def cmd1(profile):
            return profile

        @click.command()
        @_add_profile_detection
        def cmd2(profile):
            return profile

        # Both should return exactly the same object
        profile_1 = cmd1([], standalone_mode=False)
        assert profile_1 is cmd2([], standalone_mode=False)

        # But after reset the object should be different but with the same content
        _add_profile_detection.reset()
        profile_2 = cmd2([], standalone_mode=False)
        assert profile_1 is not profile_2
        assert profile_1 == profile_2

        # Demanding another file should be ignored and print a warning
        with open("fake.toml", "x"):
            pass  # Option expects an existing file
        profile_3 = cmd2(["-p", "fake.toml"], standalone_mode=False)
        assert profile_2 is profile_3
        stdout, stderr = capsys.readouterr()
        assert "Warning" in stdout
        assert "but already using" in stdout

    def test_validation(self, tmp_path):
        """Check behavior for invalid profiles and --no-validation option."""
        os.chdir(tmp_path)
        create_profile_file("ptvpy.toml", data_files="invalid")

        @click.command()
        @AddProfileDetection()
        def cmd(profile):
            return profile

        error_msg = (
            "'ptvpy.toml' is not a valid profile:\n"
            "    general.data_files: must match at least once and never a directory"
        )
        with pytest.raises(ValidationError) as exc_info:
            cmd([], standalone_mode=False)
        assert exc_info.value.message == error_msg
        assert exc_info.value.hint is None

        profile = cmd(["--no-validation"], standalone_mode=False)
        assert isinstance(profile, Profile)
        assert not profile.is_valid

    def test_profile_option(self, fresh_project):
        create_profile_file("specific.toml", data_files="*.tif*")

        @click.command()
        @AddProfileDetection()
        def cmd(profile):
            return profile

        detected = cmd([], standalone_mode=False)
        specific_1 = cmd(["-p", "specific.toml"], standalone_mode=False)
        specific_2 = cmd(["--profile", "specific.toml"], standalone_mode=False)
        assert "ptvpy.toml" == str(detected.path.name)
        assert "specific.toml" == str(specific_1.path.name)
        assert "specific.toml" == str(specific_2.path.name)
