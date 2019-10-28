"""Tests for the ptvpy.process module."""


import pytest
import pandas as pd
import numpy as np
from numpy.testing import assert_allclose

from ptvpy import process
from ptvpy.generate import describe_lines


class Test_xy_velocity:
    """Check function `xy_velocity`."""

    @staticmethod
    def _data(x_vel=1, y_vel=2) -> "pd.DataFrame":
        """Create testing data (helper function)."""
        particles = describe_lines(
            frame_count=20,
            particle_count=10,
            x_max=100,
            y_max=100,
            x_vel=x_vel,
            y_vel=y_vel,
            wrap=False,  # Avoid jumps in dx, dy
            seed=42,
        )
        return particles

    def test_copy(self):
        """Check that input dataframe is not modified."""
        df_in = self._data()
        df_out = process.xy_velocity(df_in)
        assert df_in is not df_out

    @pytest.mark.parametrize("step", [1, 5, 10, np.int(1)])
    def test_empty_data(self, step):
        """Check behavior for an empty DataFrame."""
        empty_data = self._data().iloc[:0, :]
        assert empty_data.shape == (0, 4)
        result = process.xy_velocity(empty_data, step)
        assert result.shape == (0, 6)

    @pytest.mark.parametrize("step", [1, 5, 10, np.int(1)])
    def test_const_velocity(self, step):
        """Check behavior for particles with constant velocity."""
        x_vel, y_vel = 1, 2
        result = process.xy_velocity(self._data(x_vel, y_vel), step)
        # Step size should have no effect with constant velocity
        assert_allclose(result["dx"].dropna(), x_vel)
        assert_allclose(result["dy"].dropna(), y_vel)
        particle_no = result["particle"].nunique()
        # Number on nans should be step * particle_no, because averaging only
        # works after skipping the first `step` rows
        assert len(result["dx"].dropna()) == len(result) - step * particle_no
        assert len(result["dy"].dropna()) == len(result) - step * particle_no

    # TODO test_linear_velocity

    @pytest.mark.parametrize("step", [1.0, 1.1, 1 + 0j, "1", None])
    def test_step_type_error(self, step):
        with pytest.raises(TypeError, match="step must be an int, was"):
            process.xy_velocity(self._data(), step)

    @pytest.mark.parametrize("step", [-1, 0, np.iinfo(np.int64).min])
    def test_step_value_error(self, step):
        with pytest.raises(ValueError, match="step must be at least 1, was"):
            process.xy_velocity(self._data(), step)


def test_find_helix_particles():
    """Simple test that compares results with reviewed DataFrames."""
    points = pd.DataFrame([(0, 0), (1, 1), (0, 2), (2, 1)], columns=("x", "y"))

    pairs = process.find_helix_particles(
        points, 1, np.sqrt(5), unique=False, save_old_pos=True
    )
    desired = {
        "x": [0.5, 0.0, 1.0, 0.5, 1.5, 1.0],
        "y": [0.5, 1.0, 0.5, 1.5, 1.0, 1.5],
        "x_old_1": [0, 0, 0, 1, 1, 0],
        "x_old_2": [1, 0, 2, 0, 2, 2],
        "y_old_1": [0, 0, 0, 1, 1, 2],
        "y_old_2": [1, 2, 1, 2, 1, 1],
        "angle": [np.pi / 4, np.pi / 2, np.arctan(0.5), -np.pi / 4, 0, -np.arctan(0.5)],
        "pair_distance": [np.sqrt(2), 2, np.sqrt(5), np.sqrt(2), 1, np.sqrt(5)],
    }
    pd.testing.assert_frame_equal(pairs, pd.DataFrame(desired))

    # Demanding that each particle only appears once should return two pairs
    pairs = process.find_helix_particles(points, 0, 100, unique=True)
    desired = {
        "x": [1.5, 0.0],
        "y": [1.0, 1.0],
        "angle": [0.0, np.pi / 2],
        "pair_distance": [1.0, 2.0],
    }
    pd.testing.assert_frame_equal(pairs, pd.DataFrame(desired))

    # Increasing the minimum distance should force different pairs
    pairs = process.find_helix_particles(points, np.sqrt(2), 100, unique=True)
    desired = {
        "x": [0.5, 1.0],
        "y": [0.5, 1.5],
        "angle": [np.pi / 4, -np.arctan(0.5)],
        "pair_distance": [np.sqrt(2), np.sqrt(5)],
    }
    pd.testing.assert_frame_equal(pairs, pd.DataFrame(desired))
