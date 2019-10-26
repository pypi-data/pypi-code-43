"""Utils module tests unit."""
import pytest as pt
import numpy as np

from ..utils import check_distance_matrix, is_symmetric


class TestCheckDistanceMatrix:

    not_square_matrix_test_data = [
            pt.param(np.zeros((1, 2)), marks=pt.mark.xfail),
            pt.param(np.ones((2, 3)), marks=pt.mark.xfail),
            pt.param(np.zeros((5, 4)), marks=pt.mark.xfail),
            pt.param(np.ones((3, 9)), marks=pt.mark.xfail),
            pt.param(np.zeros((10, 2)), marks=pt.mark.xfail),
            pt.param(np.ones((5, 6)), marks=pt.mark.xfail),
            ]

    @pt.mark.parametrize("matrix", not_square_matrix_test_data)
    def test_raise_value_error_for_not_square_matrices(self, matrix):
        check_distance_matrix(matrix)

    not_symmetric_matrix_test_data = [
            pt.param(np.random.random(size=(2, 2)), marks=pt.mark.xfail),
            pt.param(np.random.random(size=(3, 3)), marks=pt.mark.xfail),
            pt.param(np.random.random(size=(4, 4)), marks=pt.mark.xfail),
            pt.param(np.random.random(size=(5, 5)), marks=pt.mark.xfail),
            pt.param(np.random.random(size=(6, 6)), marks=pt.mark.xfail),
            pt.param(np.random.random(size=(7, 7)), marks=pt.mark.xfail),
            ]

    @pt.mark.parametrize("matrix", not_symmetric_matrix_test_data)
    def test_raise_value_error_for_not_symmetric_matrices(self, matrix):
        check_distance_matrix(matrix)

    square_symmetric_matrix_test_data = [
            np.zeros((2, 2)),
            np.ones((2, 2)),
            np.zeros((3, 3)),
            np.ones((3, 3))
            ]

    @pt.mark.parametrize("matrix", square_symmetric_matrix_test_data)
    def test_symmetric_and_square_matrices(self, matrix):
        check_distance_matrix(matrix)

    negative_entry_matrix_test_data = [
            pt.param(np.array([[-1, 0], [0, -1]]), marks=pt.mark.xfail),
            ]

    @pt.mark.parametrize("matrix", negative_entry_matrix_test_data)
    def test_raise_value_error_for_nagative_entry_matrices(self, matrix):
        check_distance_matrix(matrix)


class TestIsSymmetric:

    matrix_examples = [
            (np.zeros((2, 2)), True),
            (np.ones((2, 2)), True),
            (np.zeros((3, 3)), True),
            (np.ones((3, 3)), True),
            (np.random.random((10, 10)), False),
            (np.random.random((11, 11)), False),
            ]

    @pt.mark.parametrize("matrix,expected", matrix_examples)
    def test_is_symmetric_matrices(self, matrix, expected):
        assert is_symmetric(matrix) == expected
