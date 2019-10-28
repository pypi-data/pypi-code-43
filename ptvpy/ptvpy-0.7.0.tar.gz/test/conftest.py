"""Fixtures and tools to test the CLI."""


import os
import shutil
import tempfile
import warnings
from pathlib import Path
from datetime import datetime

import pytest
import tifffile
import trackpy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from click.testing import CliRunner

from ptvpy import generate, process, io, _profile, _cli_root


# Ensure that trackpy doesn't log messages
trackpy.quiet()


# TODO Use autodirctive to switch CWD in doctests?
#  https://stackoverflow.com/a/46991331/8483989


@pytest.fixture(scope="function")
def close_plots():
    """Closes all open matplotlib figures when the test function exits."""
    yield
    plt.close("all")


@pytest.fixture(scope="session")
def _temporary_directory():
    """Provide session specific directory for the static project fixtures.

    Is deleted when the session terminates.

    See Also
    --------
    static_fresh_project, static_full_project
    """
    tmp_dir = Path(tempfile.mkdtemp())
    try:
        yield tmp_dir
    finally:
        shutil.rmtree(tmp_dir)


@pytest.fixture(scope="session")
def _fresh_project(_temporary_directory):
    """Provides a session-specific project directory without processing results.

    Using the static version where possible reduces the execution time and disk
    space needed by tests that use this fixture.

    Parameters
    ----------
    _temporary_directory : Path
        Path to a session specific temporary directory.

    Returns
    -------
    static_fresh_project : Path
        Path to a session specific readonly project directory.
    """
    seed = 42
    static_dir = _temporary_directory / "fresh_project"
    static_dir.mkdir()

    particles = generate.describe_lines(
        frame_count=20,
        particle_count=20,
        x_max=200,
        y_max=200,
        x_vel=1,
        y_vel=0,
        seed=seed,
    )
    generate.add_properties(particles, seed=seed, inplace=True)
    frames = generate.render_frames(particles, background=np.zeros((200, 200)))
    path_template = "image_{:0>2}.tiff"
    for i, frame in enumerate(frames):
        # Ensure that allowed value range of storage format is not exceeded
        frame = frame.round().clip(0, 255).astype(np.uint8)
        tifffile.imsave(
            static_dir / path_template.format(i),
            frame,
            # TIFF format stores a timestamp, to make the hash consistent we
            # need to enforce the date
            datetime=datetime(2019, 10, 24),
        )
    # Create matching profile file
    _profile.create_profile_file(
        static_dir / _profile.DEFAULT_PROFILE_NAME, data_files="image_*.tiff"
    )

    return static_dir


@pytest.fixture(scope="function")
def fresh_project(tmp_path, _fresh_project):
    """Provides a project directory without processing results.

    Consider using the the static version which reduces the execution time and
    disk space needed by tests that use this fixture.

    Parameters
    ----------
    tmp_path : Path
        Path to a function specific temporary directory.
    _fresh_project : Path
        Path to a session specific readonly project directory.

    Returns
    -------
    fresh_project : Path
        Path to the new function specific project directory.
    """
    tmp_path.rmdir()  # copytree expects to create target dir
    shutil.copytree(_fresh_project, tmp_path)
    os.chdir(tmp_path)

    # Ensure that the generated content of this fixture is always the same
    digest = io.hash_files(Path(".").glob("**/*"), hash_names=True)
    # The digest depends on the newline separator used when creating a new
    # profile file
    known_digests = {
        "\n": "62cc5d875caa6483ecde6e231711662a81f7b9ae",
        "\r\n": "750d8663ae3a3fe41c75d8e71bf5c35b9f8aeb5b",
    }
    if digest != known_digests[os.linesep]:
        warnings.warn(
            f"unknown hash {digest!r} for files created by the fresh_project fixture"
        )

    return tmp_path


@pytest.fixture(scope="session")
def _full_project(_fresh_project, _temporary_directory):
    """Provides a session-specific project directory with processing results.

    Using the static version where possible reduces the execution time and disk
    space needed by tests that use this fixture.

    Parameters
    ----------
    _fresh_project : Path
        Path to a session specific readonly project directory.
    _temporary_directory : Path
        Path to a session specific temporary directory.

    Returns
    -------
    static_fresh_project : Path
        Path to a session specific readonly project directory.
    """
    static_dir = _temporary_directory / "full_project"
    assert not static_dir.exists()

    shutil.copytree(_fresh_project, static_dir)

    # Change to new directory and autodetect
    os.chdir(static_dir)
    profile = _profile.Profile(static_dir / _profile.DEFAULT_PROFILE_NAME)

    # Lazy-load Frames
    loader = io.FrameLoader(
        pattern=profile["general.data_files"],
        slice_=slice(*profile["general.subset"][["start", "stop", "step"]]),
    )
    storage_file = profile["general.storage_file"]
    if profile["step_locate.remove_background"]:
        loader.remove_background(storage_file)
    frames = loader.lazy_frame_sequence()

    # Locate particles
    particles = []
    for i, frame in enumerate(frames):
        result = trackpy.locate(frame, **profile["step_locate.trackpy_locate"])
        result["frame"] = i
        particles.append(result)
    particles = pd.concat(particles, ignore_index=True)

    # Link particles
    particles = trackpy.link(particles, **profile["step_link.trackpy_link"])
    particles = trackpy.filter_stubs(
        particles, **profile["step_link.trackpy_filter_stubs"]
    )
    particles.reset_index(drop=True, inplace=True)

    # Calculate velocities
    particles = process.xy_velocity(particles, profile["step_diff.diff_step"])
    particles = process.absolute_velocity(particles)

    # Store the content
    with io.Storage(static_dir / Path(storage_file).name, "a") as file:
        file.save_df("particles", particles)

    return static_dir


@pytest.fixture(scope="function")
def full_project(tmp_path, _full_project):
    """Provides a project directory with processing results.

    Consider using the the static version which reduces the execution time and
    disk space needed by tests that use this fixture.

    Parameters
    ----------
    tmp_path : Path
        Path to a function specific temporary directory.
    _full_project : Path
        Path to a session specific readonly project directory.

    Returns
    -------
    static_fresh_project : Path
        Path to the new function specific project directory.
    """
    tmp_path.rmdir()  # copytree expects to create target dir
    shutil.copytree(_full_project, tmp_path)
    os.chdir(tmp_path)

    # Some sanity checks
    with io.Storage(tmp_path / "ptvpy.h5", "r") as file:
        assert len(file["particles"]) > 0
        assert "background" in file

    return tmp_path


@pytest.fixture(scope="session")
def runner():
    """Session specific runner to execute PtvPy's console commands.

    Returns
    -------
    runner : callable
        Signature is the same as :func:`click.testing.CliRunner.invoke` without
        the first argument `cli`.
    """
    # TODO Currently, it's not possible to check if PtvPy writes to stderr.
    #  This is because Exceptions are only displayed in stderr after the
    #  command has run in the wrapping _cli_root.main method.
    runner = CliRunner(mix_stderr=False)

    def run(*args, **kwargs):
        return runner.invoke(_cli_root.root_group, *args, **kwargs)

    return run
