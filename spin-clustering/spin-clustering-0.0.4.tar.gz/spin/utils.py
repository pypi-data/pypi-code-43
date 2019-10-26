"""Utility functions to support other modules."""

import numpy as np


def check_distance_matrix(distances):
    """Perform all tests to check if the distance matrix is correct.

    Check if the distances matrix provided respects all constraints a distance
    matrix must have.

    Parameters
    ----------
    distances: array, shape (n_points, n_points)
        The distances symmetric square matrix.

    """
    # square matrix check
    if distances.shape[0] != distances.shape[1]:
        raise ValueError("Distance matrix provided is not square. "
                         f"The shape provided is {distances.shape}")

    # symmetry check
    if not is_symmetric(distances):
        raise ValueError("Distance matrix provided is not symmetric.")

    # all positive
    if not np.all(distances >= 0):
        raise ValueError("Distances matrices must have all its entries "
                         "positive.")


def is_symmetric(matrix, rtol=1e-5, atol=1e-8):
    """Check if a matrix is symmetric.

    Parameters
    ----------
    matrix: array, shape (n, n)
        matrix to be checked.
    rtol: float, optional (default=1e-5)
        Relative tolerance.
    atol: float, optional (default=1e-8)
        Absolute tolerance.

    """
    return np.allclose(matrix, matrix.T, rtol=rtol, atol=atol)


def random_permutation_matrix(size):
    """Random permutation matrix.

    Parameters
    ----------
    size : int
        The dimension of the random permutation matrix.

    Returns
    -------
    random_permutation : array, shape (size, size)
        An identity matrix with its rows random shuffled.

    """
    identity = np.identity(size)
    index = np.arange(0, size)
    np.random.shuffle(index)
    random_permutation = identity[index]
    return random_permutation


def spin_energy(ordered_distances, weight_matrix):
    """SPIN matrix energy.

    Metrices with better sorting have lower energies.

    Parameters
    ----------
    ordered_distances : array, shape (n, n)
        The ordered distances matrix. ordered_distances = PDP.T
    weight_matrix : array, shape (n, n)
        The weight matrix to weight the ordered distances matrix.

    Returns
    -------
    energy : float
        The energy of the associated ordered distance matrix and the
        weight matrix.
    """
    energy = np.trace(ordered_distances.dot(weight_matrix))
    return energy
