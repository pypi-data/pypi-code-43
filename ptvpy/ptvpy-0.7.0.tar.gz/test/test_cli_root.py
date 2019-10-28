"""Test the Command line interface of PtvPy."""


import os

import click
import pytest
import pandas as pd
import matplotlib.pyplot as plt
from numpy.testing import assert_allclose
from scipy.io import loadmat

from ptvpy import _cli_root


plt.ion()  # Enable interactive mode, so that plotting doesn't block


def test_basic_workflow(tmp_path, runner):
    """Test the basic workflow using the command line."""
    os.chdir(tmp_path)

    # Generate synthetic images (supply image-nr with prompt)
    result = runner("generate lines --seed 42 -- data/ 20")
    assert result.exit_code == 0
    assert len(list(tmp_path.glob("data/image_??.tiff"))) == 20

    # Create a profile file
    result = runner("profile create --data-files data/*.tif*")
    assert result.exit_code == 0
    assert os.path.isfile("ptvpy.toml")

    # And check
    result = runner("profile check")
    assert result.exit_code == 0
    assert "is a valid profile" in result.output

    # Process images
    result = runner("process")
    assert result.exit_code == 0
    assert os.path.isfile("ptvpy.h5")

    # View images
    result = runner("view summary scatter3d x size v")
    assert result.exit_code == 0

    # Export data
    result = runner("export data.csv")
    assert result.exit_code == 0

    # Check exported data
    exported = pd.read_csv("data.csv")
    assert exported.shape == (317, 14)
    assert exported["frame"].unique().size == 20
    assert exported["particle"].unique().size == 17

    # Canary to detect subtle changes (doesn't actually test correctness)
    # Created with print(np.array(exported[["y", "x", "v"]].describe([])).tolist())
    assert_allclose(
        exported[["y", "x", "v"]].describe([]),
        [
            [317.0, 317.0, 300.0],
            [86.23137342693911, 97.16578028804352, 2.0441164102176437],
            [52.077874962721154, 53.024551440895415, 0.42124643625232217],
            [8.961285781323323, 6.013735589894531, 1.958464580235529],
            [88.03321878579611, 92.8477157360406, 2.0016356847810295],
            [193.44580152671762, 194.5041694838855, 9.294820766693713],
        ],
    )


def test_export(full_project, runner):
    """Basic tests for export command."""
    assert runner("export test.csv").exit_code == 0
    assert os.path.isfile("./test.csv")
    data = pd.read_csv("./test.csv")
    assert data.shape == (319, 14)

    assert runner("export test.xlsx").exit_code == 0
    assert os.path.isfile("./test.xlsx")

    assert runner("export test.mat").exit_code == 0
    assert os.path.isfile("./test.mat")
    data = loadmat("./test.mat")
    assert len(data.keys()) == 16  # + 3 meta variables
    for key, value in data.items():
        if key.startswith("_"):
            continue
        assert value.size == 319

    assert runner("export test.sqlite").exit_code == 0
    assert os.path.isfile("./test.sqlite")


def test_no_validation_option(full_project, runner):
    """Check that the --force-profile option does what it promises."""
    with open("ptvpy.toml", "a") as stream:
        # Add an unsupported option that won't break anything but would fail
        # validation
        stream.write("\nunkown_option = true\n")

    result = runner("profile check")
    assert "unknown field" in result.stdout

    result = runner("process --step diff")
    assert result.exit_code == 1
    assert "is not a valid profile" in result.exception.args[0]
    # Using force option should run the command without error
    result = runner("process --no-validation --step diff")
    assert result.exit_code == 0

    result = runner("view summary")
    assert result.exit_code == 1
    assert "is not a valid profile" in result.exception.args[0]
    # Using force option should run the command without error
    result = runner("view summary --no-validation")
    assert result.exit_code == 0

    result = runner("export particles.csv")
    assert result.exit_code == 1
    assert "is not a valid profile" in result.exception.args[0]
    # Using force option should run the command without error
    result = runner("export --no-validation particles.csv")
    assert result.exit_code == 0


def test_main(capsys, monkeypatch, tmp_path):
    """Test PtvPy's main method."""
    os.chdir(tmp_path)
    # Normal usage
    _cli_root.main(args=["--version"])

    stdout, stderr = capsys.readouterr()
    assert "version" in stdout

    # With debug mode
    with monkeypatch.context() as m:
        m.setitem(os.environ, "PTVPY_DEBUG", "1")
        with pytest.raises(click.UsageError, match="No such command"):
            _cli_root.main(args=["unknown"])

    # and without debug mode
    with monkeypatch.context() as m:
        m.delitem(os.environ, "PTVPY_DEBUG")
        assert _cli_root.main(args=["unknown"]) == 1
    stdout, stderr = capsys.readouterr()
    assert '\nUsageError: No such command "unknown".\n' == stderr
    assert (
        "\nAppend '-h' for help or retry with 'ptvpy --debug ...' to show the "
        "traceback.\n"
    ) in stdout


def test_documentation_option(runner, monkeypatch):
    def mock_launch(*args, **kwargs):
        setattr(mock_launch, "args", args)
        setattr(mock_launch, "kwargs", kwargs)

    with monkeypatch.context() as m:
        m.setattr(click, "launch", mock_launch)
        result = runner("--documentation")

    assert result.exit_code == 0
    assert mock_launch.args == ("https://tud-mst.gitlab.io/ptvpy",)
    assert mock_launch.kwargs == {"wait": False}
