import pytest
import numpy as np
from .rotation import rotation_from_up_and_look, euler


def test_starting_with_canonical_reference_frame_gives_identity():
    result = rotation_from_up_and_look(up=[0, 1, 0], look=[0, 0, 1])
    np.testing.assert_array_almost_equal(result, np.eye(3))


def test_raises_value_error_with_zero_length_inputs():
    with pytest.raises(ValueError):
        rotation_from_up_and_look(up=[0, 0, 0], look=[0, 0, 1])
    with pytest.raises(ValueError):
        rotation_from_up_and_look(up=[0, 1, 0], look=[0, 0, 0])


def test_raises_value_error_with_collinear_inputs():
    with pytest.raises(ValueError):
        rotation_from_up_and_look(up=[0, 0, 1], look=[0, 0, 1])
    with pytest.raises(ValueError):
        rotation_from_up_and_look(up=[0, 0, 1], look=[0, 0, -1])


def test_normalizes_inputs():
    result = rotation_from_up_and_look(up=[0, 42, 0], look=[0, 0, 13])
    np.testing.assert_array_almost_equal(result, np.eye(3))


def test_always_outputs_float64():
    result = rotation_from_up_and_look(
        up=np.array([0, 1, 0], dtype=np.float32),
        look=np.array([0, 0, 1], dtype=np.float32),
    )
    assert result.dtype == np.float64
    np.testing.assert_array_almost_equal(result, np.eye(3))


def test_vary_look_alone():
    np.testing.assert_array_almost_equal(
        euler([0, 45]), rotation_from_up_and_look(up=[0, 1, 0], look=[-1, 0, 1])
    )
    np.testing.assert_array_almost_equal(
        euler([0, 90]), rotation_from_up_and_look(up=[0, 1, 0], look=[-1, 0, 0])
    )
    np.testing.assert_array_almost_equal(
        euler([0, 135]), rotation_from_up_and_look(up=[0, 1, 0], look=[-1, 0, -1])
    )
    np.testing.assert_array_almost_equal(
        euler([0, 180]), rotation_from_up_and_look(up=[0, 1, 0], look=[0, 0, -1])
    )
    np.testing.assert_array_almost_equal(
        euler([0, 225]), rotation_from_up_and_look(up=[0, 1, 0], look=[1, 0, -1])
    )
    np.testing.assert_array_almost_equal(
        euler([0, 270]), rotation_from_up_and_look(up=[0, 1, 0], look=[1, 0, 0])
    )
    np.testing.assert_array_almost_equal(
        euler([0, 315]), rotation_from_up_and_look(up=[0, 1, 0], look=[1, 0, 1])
    )


def test_vary_up_alone():
    np.testing.assert_array_almost_equal(
        euler([0, 0, 45]), rotation_from_up_and_look(up=[1, 1, 0], look=[0, 0, 1])
    )
    np.testing.assert_array_almost_equal(
        euler([0, 0, 90]), rotation_from_up_and_look(up=[1, 0, 0], look=[0, 0, 1])
    )
    np.testing.assert_array_almost_equal(
        euler([0, 0, 135]), rotation_from_up_and_look(up=[1, -1, 0], look=[0, 0, 1])
    )
    np.testing.assert_array_almost_equal(
        euler([0, 0, 180]), rotation_from_up_and_look(up=[0, -1, 0], look=[0, 0, 1])
    )
    np.testing.assert_array_almost_equal(
        euler([0, 0, 225]), rotation_from_up_and_look(up=[-1, -1, 0], look=[0, 0, 1])
    )
    np.testing.assert_array_almost_equal(
        euler([0, 0, 270]), rotation_from_up_and_look(up=[-1, 0, 0], look=[0, 0, 1])
    )
    np.testing.assert_array_almost_equal(
        euler([0, 0, 315]), rotation_from_up_and_look(up=[-1, 1, 0], look=[0, 0, 1])
    )


# Look up rotation matrices on wikipedia and you too can work these out by hand...
def test_x():
    s2 = np.sqrt(2) / 2
    np.testing.assert_array_almost_equal(euler(0), np.eye(3))
    np.testing.assert_array_almost_equal(
        euler(45), np.array([[1, 0, 0], [0, s2, -s2], [0, s2, s2]])
    )
    np.testing.assert_array_almost_equal(
        euler(90), np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
    )
    np.testing.assert_array_almost_equal(
        euler(180), np.array([[1, 0, 0], [0, -1, -0], [0, 0, -1]])
    )
    np.testing.assert_array_almost_equal(
        euler(270), np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
    )
    np.testing.assert_array_almost_equal(euler(360), np.eye(3))
    np.testing.assert_array_almost_equal(euler(0 * np.pi, units="rad"), np.eye(3))
    np.testing.assert_array_almost_equal(
        euler(0.25 * np.pi, units="rad"),
        np.array([[1, 0, 0], [0, s2, -s2], [0, s2, s2]]),
    )
    np.testing.assert_array_almost_equal(
        euler(0.5 * np.pi, units="rad"), np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
    )
    np.testing.assert_array_almost_equal(
        euler(1 * np.pi, units="rad"), np.array([[1, 0, 0], [0, -1, -0], [0, 0, -1]])
    )
    np.testing.assert_array_almost_equal(
        euler(1.5 * np.pi, units="rad"), np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
    )
    np.testing.assert_array_almost_equal(euler(2 * np.pi, units="rad"), np.eye(3))


def test_y():
    s2 = np.sqrt(2) / 2
    np.testing.assert_array_almost_equal(euler([0, 0]), np.eye(3))
    np.testing.assert_array_almost_equal(
        euler([0, 45]), np.array([[s2, 0, s2], [0, 1, 0], [-s2, 0, s2]])
    )
    np.testing.assert_array_almost_equal(
        euler([0, 90]), np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]])
    )
    np.testing.assert_array_almost_equal(
        euler([0, 180]), np.array([[-1, 0, 0], [0, 1, 0], [-0, 0, -1]])
    )
    np.testing.assert_array_almost_equal(
        euler([0, 270]), np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]])
    )
    np.testing.assert_array_almost_equal(euler([0, 360]), np.eye(3))
    np.testing.assert_array_almost_equal(euler([0, 0 * np.pi], units="rad"), np.eye(3))
    np.testing.assert_array_almost_equal(
        euler([0, 0.25 * np.pi], units="rad"),
        np.array([[s2, 0, s2], [0, 1, 0], [-s2, 0, s2]]),
    )
    np.testing.assert_array_almost_equal(
        euler([0, 0.5 * np.pi], units="rad"),
        np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]]),
    )
    np.testing.assert_array_almost_equal(
        euler([0, 1 * np.pi], units="rad"),
        np.array([[-1, 0, 0], [0, 1, 0], [-0, 0, -1]]),
    )
    np.testing.assert_array_almost_equal(
        euler([0, 1.5 * np.pi], units="rad"),
        np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]]),
    )
    np.testing.assert_array_almost_equal(euler([0, 2 * np.pi], units="rad"), np.eye(3))


def test_z():
    s2 = np.sqrt(2) / 2
    np.testing.assert_array_almost_equal(euler([0, 0, 0]), np.eye(3))
    np.testing.assert_array_almost_equal(
        euler([0, 0, 45]), np.array([[s2, -s2, 0], [s2, s2, 0], [0, 0, 1]])
    )
    np.testing.assert_array_almost_equal(
        euler([0, 0, 90]), np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
    )
    np.testing.assert_array_almost_equal(
        euler([0, 0, 180]), np.array([[-1, 0, 0], [0, -1, 0], [0, 0, 1]])
    )
    np.testing.assert_array_almost_equal(
        euler([0, 0, 270]), np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]])
    )
    np.testing.assert_array_almost_equal(euler([0, 0, 360]), np.eye(3))
    np.testing.assert_array_almost_equal(
        euler([0, 0, 0 * np.pi], units="rad"), np.eye(3)
    )
    np.testing.assert_array_almost_equal(
        euler([0, 0, 0.25 * np.pi], units="rad"),
        np.array([[s2, -s2, 0], [s2, s2, 0], [0, 0, 1]]),
    )
    np.testing.assert_array_almost_equal(
        euler([0, 0, 0.5 * np.pi], units="rad"),
        np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]]),
    )
    np.testing.assert_array_almost_equal(
        euler([0, 0, 1 * np.pi], units="rad"),
        np.array([[-1, 0, 0], [0, -1, 0], [0, 0, 1]]),
    )
    np.testing.assert_array_almost_equal(
        euler([0, 0, 1.5 * np.pi], units="rad"),
        np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]]),
    )
    np.testing.assert_array_almost_equal(
        euler([0, 0, 2 * np.pi], units="rad"), np.eye(3)
    )


# Really should write some tests for composition...
