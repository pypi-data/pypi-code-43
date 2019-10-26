"""Neighborhood SPIN Module."""
import numpy as np
import matplotlib.pyplot as plt
from .utils import check_distance_matrix, spin_energy


class NeighborhoodSPIN():
    """Neighborhood SPIN clustering method.

    Parameters
    ----------
    initial_sigma : float, optional (default=2e10)
        Initial sigma value. This parameter controls the weight matrix
        dispersion.
    update_factor : float, optional (default=0.5)
        The number that will update the sigma value at each iteration. Sigma
        will be updated by sigma = sigma * update_factor.
    max_iter : int, optional (default=100)
        The maximum number of iterations of each round of sorting.
    verbose : boolean, optional (default=False)
        Flag indicating to show logs and information during the SPIN process.

    Attributes
    ----------
    distances_ : array, shape (n, n)
        The original distances matrix provided.
    permutation_ : array, shape (n, n)
        Permutation matrix that can be applied to the original distances matrix
        to get to the ordered distances matrix.
    ordered_distances_ : array, shape (n, n)
        Distances matrix reordered by the permutation matrix. Before run this
        is the original distance matrix.

    References
    ----------
    D. Tsafrir, I. Tsafrir, L. Ein-Dor, O. Zuk, D.A. Notterman, E. Domany,
        Sortiug points into neighborhoods (SPIN): data analysis and
        visualization by ordering distance matrices, Bioinformatics, Volume 21,
        Issue 10, , Pages 2301–2308,
        https://doi.org/10.1093/bioinformatics/bti329

    """

    def __init__(self, intial_sigma=2**10, update_factor=0.5, max_iter=100,
                 verbose=False):
        self.intial_sigma = intial_sigma
        self.update_factor = update_factor
        self.max_iter = max_iter
        self.verbose = verbose

    def run(self, X):
        """Execute the Neighborhood sorting.

        Parameters
        ----------
        X : array, shape (n, n)

        Returns
        -------
        self : NeighborhoodSPIN
            The object itself containing the ordered distances matrix.

        """
        check_distance_matrix(X)

        self.size_ = X.shape[0]
        self.distances_ = X
        self.permutation_ = np.identity(self.size_)
        self.ordered_distances_ = self.permutation_.dot(self.distances_) \
                                                   .dot(self.permutation_.T)
        sigma = self.intial_sigma
        while sigma > 1:
            weight_matrix = initial_weight_matrix(self.size_, sigma)
            permutation = neighborhood(self.ordered_distances_,
                                       weight_matrix,
                                       self.max_iter,
                                       self.verbose)
            plt.matshow(permutation)
            self.ordered_distances_ = permutation.dot(self.ordered_distances_)\
                                                 .dot(permutation.T)
            plt.matshow(self.ordered_distances_)
            self.permutation_ = permutation.dot(self.permutation_)
            sigma = sigma * self.update_factor
        return self


def neighborhood(distances, weight_matrix, max_iter=100, verbose=False):
    """Neighborhood SPIN algorithm.

    Parameters
    ----------
    distances : np.array, shape [n, n]
        Distance symmetric square matrix.
    weight_matrix : np.array, shape [n, n]
        A initial weight matrix to update permutaions matrix.
    max_iter : int, default=100
        Maximum number of iterations.
    verbose : bool
        Verbosity flag, if it is true print useful information about the
        process.

    Returns
    -------
    permutation : np.array, shape [n, n]
        Permutation matrix with the same dimensions of the distance matrix.

    """
    permutation = np.identity(distances.shape[0])
    mismatch_matrix = distances.dot(weight_matrix)
    trace = np.trace(permutation.dot(mismatch_matrix))
    for i in range(max_iter):
        (new_permutation,
         new_mismatch) = single_neighborhood_sort(distances, weight_matrix)
        new_trace = np.trace(new_permutation.dot(new_mismatch))
        if new_trace == trace:
            break
        weight_matrix = new_permutation.T.dot(weight_matrix)
        trace = new_trace
    return new_permutation


def single_neighborhood_sort(distances, weight_matrix):
    """Single stage on the neighborhood sorting process.

    Parameters
    ----------
    distances : array, shape (n, n)
        The distances matrix to be sorted.
    weight_matrix : array, shape (n, n)
        The weight matrix to take into in account in sorting. The distribuition
        on the matrix values control the scale of the sorting operations.

    """
    size = len(distances)
    mismatch = distances.dot(weight_matrix)
    min_index = np.argmin(mismatch, axis=1)
    min_values = mismatch[np.arange(size), idx_m]
    max_value = max(min_values)
    sort_score = (min_index + 1.
                  - 0.1 * np.sign((size / 2. - min_index + 1.)) *
                  min_values / max_value)
    sorted_ind = np.argsort(sort_score)
    permutation = np.identity(distances.shape[0])[sorted_ind]
    return permutation, mismatch


def initial_weight_matrix(size, sigma=1e2):
    """Initialize the weight matrix for neighborhood method.

    This initial matrix is initialized with exponential coefficients and then
    turned into a doubly stochastic matrix.

    Parameters
    ----------
    size : int
        The size of the initial weight matrix.
    sigma : float, optional, (default=1e2)
        Coefficient to control dispersion of the weigth metrix coefficients.

    Returns
    -------
    weight_matrix : array, shape (size, size)
        The initial weight matrix. It is a square matrix.

    """
    rows_index_matrix, columns_index_matrix = np.indices((size, size))
    diff_index_matrix = rows_index_matrix - columns_index_matrix
    exp_arg_index_matrix = -(diff_index_matrix**2)/(size*sigma)
    non_normalized_weight_matrix = np.exp(exp_arg_index_matrix)
    weight_matrix = sinkhorn_knopp_normalization_alogrithm(
            non_normalized_weight_matrix
            )
    return weight_matrix


def sinkhorn_knopp_normalization_alogrithm(matrix, tolerance=1e-5,
                                           max_iter=1000):
    """Turn matrices into doubly stochastic matrices.

    Turn matrices into doubly stochastic matrix through the Sinkhorn Knopp
    algorithm.

    Parameters
    ----------
    matrix : array
        The matrix that will be normalized.
    tolerance : float
        The tolerance in the matrix approximation.
    max_iter : int
        If the tolerance is not reached this argument will set the maximun
        number of iterations.

    Returns
    -------
    norm_matrix : array
        The normalized version from the original matrix.

    References
    ----------
    Sinkhorn, Richard. A Relationship Between Arbitrary Positive Matrices and
        Doubly Stochastic Matrices. Ann. Math. Statist. 35 (1964), no. 2,
        876--879.  doi:10.1214/aoms/1177703591.
        https://projecteuclid.org/euclid.aoms/1177703591

    Sinkhorn, Richard, and Paul Knopp. "Concerning nonnegative matrices and
        doubly stochastic matrices." Pacific Journal of Mathematics 21.2
        (1967): 343-348.
        http://www.yaroslavvb.com/papers/sinkhorn-concerning.pdf
    """
    norm_matrix = matrix.copy()
    for i in range(max_iter):
        col_sum = norm_matrix.sum(axis=0)
        norm_matrix = norm_matrix/col_sum
        row_sum = norm_matrix.sum(axis=1).reshape(-1, 1)
        norm_matrix = norm_matrix/row_sum

        if (np.all(np.abs(norm_matrix.sum(axis=1) - 1) < tolerance) and
           np.all(np.abs(norm_matrix.sum(axis=0) - 1) < tolerance)):
            break
    return norm_matrix
