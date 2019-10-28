"""Test cli_view module.

Currently the tests in this module are very basic and only check if the given
command will execute successfully (exit code of 0).

Uses fixtures in "test/conftest.py".
"""


import os

import pytest
import matplotlib.pyplot as plt


# Check if the tests are run in continuous integration (used to skip certain tests)
running_ci = bool(os.environ.get("CI"))

plt.ion()  # Enable interactive mode, so that plotting doesn't block

# Add fixtures used implicitly in all functions
pytestmark = pytest.mark.usefixtures("close_plots")


class TestSubcommands:
    """Test subcommands."""

    @pytest.mark.parametrize(
        "subcommand",
        [
            "",  # Test view command itself
            "background",
            "heatmap",
            "histogram",
            "scatter2d",
            "scatter3d",
            "slideshow",
            "subpixel",
            "summary",
            "trajectories",
            "vector",
            "violin",
        ],
    )
    def test_help_option(self, runner, subcommand):
        result = runner(f"view {subcommand} -h")
        assert result.exit_code == 0
        result = runner(f"view {subcommand} --help")
        assert result.exit_code == 0

    def test_background(self, runner, full_project):
        result = runner("view background")
        assert result.exit_code == 0
        assert len(plt.get_fignums()) == 1

    def test_histogram(self, runner, full_project):
        result = runner("view histogram x")
        assert result.exit_code == 0
        assert len(plt.get_fignums()) == 1

    def test_heatmap(self, runner, full_project):
        result = runner("view heatmap x y v")
        assert result.exit_code == 0
        result = runner("view heatmap --extrapolate x y v")
        assert result.exit_code == 0
        assert len(plt.get_fignums()) == 2

    def test_scatter2d(self, runner, full_project):
        result = runner("view scatter2d size mass")
        assert result.exit_code == 0
        assert len(plt.get_fignums()) == 1

    def test_scatter3d(self, runner, full_project):
        result = runner("view scatter3d x y v")
        assert result.exit_code == 0
        result = runner("view scatter3d --color size x y v")
        assert result.exit_code == 0
        assert len(plt.get_fignums()) == 2

    def test_slideshow(self, runner, full_project):
        result = runner("view slideshow")
        assert result.exit_code == 0
        result = runner("view slideshow --autostart")
        assert result.exit_code == 0
        result = runner("view slideshow --no-annotation")
        assert result.exit_code == 0
        assert len(plt.get_fignums()) == 3

    def test_slideshow_empty(self, runner, fresh_project):
        # Check that slideshow works even without results
        result = runner("view slideshow")
        assert result.exit_code == 0

    def test_subpixel(self, runner, full_project):
        result = runner("view subpixel")
        assert result.exit_code == 0
        assert len(plt.get_fignums()) == 1

    def test_summary(self, runner, full_project):
        result = runner("view summary")
        assert result.exit_code == 0

    def test_trajectories(self, runner, full_project):
        result = runner("view trajectories")
        assert result.exit_code == 0
        result = runner("view trajectories --names dx dy")
        assert result.exit_code == 0
        assert len(plt.get_fignums()) == 2

    def test_vector(self, runner, full_project):
        result = runner("view vector x y dx dy")
        assert result.exit_code == 0
        result = runner("view vector --extrapolate x y dx dy")
        assert result.exit_code == 0
        assert len(plt.get_fignums()) == 2

    def test_violin(self, runner, full_project):
        result = runner("view violin x y")
        assert result.exit_code == 0
        assert len(plt.get_fignums()) == 1

    def test_chained_commands(self, runner, full_project):
        result = runner("view summary scatter3d --color size x y v slideshow")
        assert result.exit_code == 0
        assert len(plt.get_fignums()) == 2


def test_profile_option(runner, full_project):
    os.rename("ptvpy.toml", "profile.hidden")
    # Verify auto-detection fails
    result = runner("view slideshow")
    assert result.exit_code != 0
    assert "no file matching" in result.exception.args[0]
    # and works if profile is specified
    result = runner("view slideshow -p profile.hidden")
    assert result.exit_code == 0
    result = runner("view slideshow --profile profile.hidden")
    assert result.exit_code == 0
    # and is even used by the second chained command
    result = runner("view slideshow -p profile.hidden subpixel")
    assert result.exit_code == 0
    # but prints a warning if option is passed again
    with open("fake.toml", "x"):
        pass  # Option expects an existing file
    result = runner("view slideshow -p profile.hidden subpixel -p fake.toml")
    assert result.exit_code == 0
    assert (
        "Warning: requested profile 'fake.toml' but already using 'profile.hidden'"
        in result.stdout
    )


def test_load_particles(runner, fresh_project):
    result = runner("view scatter2d x y")
    assert result.exit_code == 1
    assert "does not exist" in result.exception.args[0]
    assert "Generate data with" in result.exception.hint

    runner("view background")  # Creates ptvpy.h5 implicitly
    assert (fresh_project / "ptvpy.h5").is_file()

    result = runner("view scatter2d x y")
    assert result.exit_code == 1
    assert "no particle data found in" in result.exception.args[0]
    assert "Generate data with" in result.exception.hint
