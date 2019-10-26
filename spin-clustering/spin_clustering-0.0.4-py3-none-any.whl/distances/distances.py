"""Distances module with utilities to compute distances."""
import numpy as np


def general_distance_matrix(X, dist_function):
    """General distance matrix with custom distance function.

    Parameters
    ----------
    X : array, shape (n, k)
        The first set of column vectors. This is a set of k vectors with
        dimension of n.
    dist_function: array, shape (n, n)
        The custom function that will calculate distance between vectors. It
        must be a two argument fucntion that returns a number.

    """
    n = X.shape[1]
    dist_matrix = np.zeros((n, n), dtype=float)
    for i in range(0, n):
        for j in range(i, n):
            dist = dist_function(X[:, i], X[:, j])
            dist_matrix[i, j] = dist
            dist_matrix[j, i] = dist


def l2_distance_matrix(X, Y):
    """Fast L2 distance matrix between two sets of columns vectors.

    The final matrix will contain the distances between all X vectors and all Y
    vectors.  For instances, if we have two sets of three dimensional vectors,
    one with 10 vectors and the second with 5 vectors, the output matrix will
    be of shape 10x5.

    Parameters
    ----------
    X : array [n, k]
        The first set of column vectors. This is a set of k vectors with
        dimension of n.

    Y : array [n, l]
        The second set of column vectors. This is a set of l vectors with
        dimension of n.

    Retruns
    -------
    distance_matrix: array [k, l]
        The matrix distance. Each element d[i, j] will represent the L2
        distance between the i-th vector from X and the j-th vector from Y.
        d[i, j] = l2_distance(X[:, i], Y[:, j])

    """
    dists = -2 * X.T.dot(Y) + \
        np.sum(X**2, axis=0) + \
        np.sum(Y**2, axis=0).reshape(1, -1).T
    dists[dists < 0] = 0
    distance_matrix = np.sqrt(dists)
    return distance_matrix


def l1_distance_matrix(X, Y):
    """Fast L1 distance matrix between two sets of columns vectors."""
    pass
