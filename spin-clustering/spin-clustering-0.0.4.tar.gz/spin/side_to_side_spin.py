"""Side to side SPIN Module."""
import numpy as np


class SideToSideSPIN():
    """Side to side SPIN clustering method.

    Parameters
    ----------
    random_starts : int, optional (default=5)
        The number of different initial random permutations that will
        generated.
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

    def __init__(self, random_starts=5, max_iter=100, verbose=False):
        self.random_starts = random_starts
        self.max_iter = max_iter
        self.verbose = verbose

    def run(self, X):
        """Execute the Side To Side sorting.

        Parameters
        ----------
        X : array, shape (n, n)

        Returns
        -------
        self : SideToSideSPIN
            The object itself containing the ordered distances matrix.

        """
        if X.shape[0] != X.shape[1]:
            raise ValueError("The SPIN method only works with square matrices."
                             f"You provided a matrix of shape {X.shape}.")
        print("Setup")
        self.size_ = X.shape[0]
        self.distances_ = X
        self.permutation_ = np.identity(self.size_)
        self.ordered_distances_ = self.permutation_.dot(X) \
                                                   .dot(self.permutation_.T)
        assert np.array_equal(self.distances_, self.ordered_distances_)
        self.increasing_vector_ = np.array([i-(self.size_+1)/2
                                           for i in range(self.size_)]) \
                                    .reshape(-1, 1)
        self.weight_matrix_ = self.increasing_vector_ \
                                  .dot(self.increasing_vector_.T)
        print(self.weight_matrix_)
        self.energy_ = spin_energy(self.ordered_distances_,
                                   self.weight_matrix_)

        print(f"Initial energy: {self.energy_}")
        print("Actual spin")
        for i in range(self.random_starts):
            initial_permutation = random_permutation(self.size_)
            print(initial_permutation[:5, :5])
            permutation = side_to_side(self.distances_,
                                       self.increasing_vector_,
                                       initial_permutation,
                                       self.max_iter,
                                       self.verbose)
            if np.array_equal(permutation, initial_permutation):
                print("They are equal.")
            ordered_distances = permutation.dot(self.distances_) \
                                           .dot(permutation.T)
            energy = spin_energy(ordered_distances, self.weight_matrix_)
            print(f"{i}: {energy}")
            if energy < self.energy_:
                self.permutation_ = permutation
                self.ordered_distances_ = ordered_distances
                self.energy_ = energy


def side_to_side(distances, strictly_increasing_vector, initial_permutation,
                 max_iter=100, verbose=False):
    """Side To Side SPIN algorithm.

    Parameters
    ----------
    distances : np.array, shape [n, n]
        Distance symmetric square matrix.
    strictly_increasing_vector : np.array, shape [n]
        A vector with strictly increasing elements with the same dimension as
        the distance matrix.
    initial_permutation : array, shape [n ,n]
        The initial permutation matrix.
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
    X = strictly_increasing_vector
    permutation = initial_permutation.copy()
    for i in range(max_iter):
        print(".", end="")
        S = distances.dot(X).flatten()
        reverse_index_sort = (S).argsort()[::-1]
        new_permutation = np.identity(distances.shape[0])[reverse_index_sort]
        if np.all(new_permutation.dot(S) == permutation.dot(S)):
            break
        permutation = new_permutation
        X = permutation.dot(X)
    return permutation
