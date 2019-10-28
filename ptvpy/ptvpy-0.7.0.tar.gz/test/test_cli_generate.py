"""Test cli_generate module."""


import os

import imageio
import pytest
import pandas as pd
import numpy as np
from scipy.ndimage import map_coordinates

from ptvpy import _cli_generate


@pytest.mark.parametrize("subcommand", ["lines", "whirlpool"])
@pytest.mark.parametrize("helix", ["--helix", ""])
def test_shared_properties(tmp_path, runner, subcommand, helix):
    """Check common properties that are shared between subcommands."""
    os.chdir(tmp_path)

    # Use seed to make result reproducable and check the code path for the
    # white-noise option without actually adding any
    cmd = f"generate {subcommand} {helix} --white-noise 1 0 --seed 1812 . 20"
    result = runner(cmd)
    assert result.exception is None
    assert len(list(tmp_path.glob("*.tiff"))) == 20

    # Attempting command a second time fails
    result = runner(cmd)
    assert type(result.exception) is _cli_generate.ImagesExistError
    assert "directory already contains files" in result.exception.args[0]

    particles = pd.read_csv(tmp_path / "particles_1812.csv")
    assert particles["frame"].nunique() == 20
    assert particles["particle"].nunique() == 20

    if helix:
        # 2 rows for each particle are created (2 * 20 * 20)
        # however rows with coordinates outside the image are removed
        assert 700 < particles.shape[0] <= 800
        assert particles.shape[1] == 8

        # Check angle and pair distance for each frame and particle
        for _, df in particles.groupby(["frame", "particle"]):
            assert df.shape[0] in (1, 2)
            if df.shape[0] == 2:
                diff = df[["x", "y"]].diff(axis=0).iloc[1:]

                # Compare actual and desired angle
                actual = np.arctan(diff["y"] / diff["x"])
                desired = df["angle"].iloc[0]
                np.testing.assert_allclose(actual, desired)

                # Compare actual and desired pair distance
                actual = np.linalg.norm(diff)
                desired = df["pair_distance"].iloc[0]
                np.testing.assert_allclose(actual, desired)
    else:
        # 1 row for each particle in each frame is created
        assert particles.shape == (400, 6)

    # Check properties of each rendered frame
    for frame, df in particles.groupby("frame"):
        image_file = tmp_path / f"image_{frame:0>2}.tiff"
        assert image_file.is_file()

        image = imageio.imread(image_file)
        assert image.shape == (200, 200)
        assert np.all((0 <= image) & (image <= 255))
        # Added white background noise with a mean of 1 and variance 0 earlier
        assert np.median(image) == 1

        # Check image brightness for particles that are not close to the image
        # border where interpolation errors are more significant
        coords = df[["y", "x"]].to_numpy()
        keep = (5 < coords.min(axis=1)) & (coords.max(axis=1) < 195)
        coords = coords[keep, :]
        actual = map_coordinates(image, coords.T)

        desired = df["brightness"].iloc[keep]
        np.testing.assert_allclose(actual, desired, atol=2)
