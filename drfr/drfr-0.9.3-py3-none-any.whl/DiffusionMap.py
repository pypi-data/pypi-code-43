from sklearn.metrics.pairwise import rbf_kernel
import numpy as np
import scipy
from scipy.spatial.distance import euclidean as euc
from sklearn import neighbors

# Begin Diffusion Map method
# TODO optimize the algorithm. current: 5s for each outlier decision

def make_diffusion_map(X, gamma=0.6, sample_rate=0.1, time_step=1):
    """
    make the diffusion map, aka diffusion coordinate matrix, given a whole dataset
    :param X:
    :param gamma:
    :param sample_rate: float, smaller than 1, best between 0.01 and 0.15
    :return: eigenvalue, eigenvector, diffusion coordinate matrix
    """
    N, _ = X.shape
    if sample_rate > 1: return
    sample_size = int(N*sample_rate)
    diff_matrix = np.zeros((sample_size, sample_size))
    # TODO to be randomized
    X = X[:sample_size]
    # k_ij_slash = compute_kij_slash(X, gamma=gamma)
    kernel = rbf_kernel(X, gamma=gamma)
    trans_matrix = kernel/np.sum(kernel, axis=0)
    eigenvalue, eigenvector = scipy.linalg.eigh(trans_matrix)
    # Diffusioin Coordinate Matrix
    eigs = np.power(eigenvalue, time_step)
    for i in range(sample_size):
        diff_matrix[i] = eigs*eigenvector[i]
    return eigenvalue, eigenvector, diff_matrix, X

def compute_diffmap_kij_slash(X, x, y, gamma=0.4, alpha=0.5):
    """

    :param X: sample dataset
    :param x:
    :param y:
    :param gamma:
    :param alpha:
    :return:
    """
    shape = X.shape
    # adapt gammas in paper and rbf_kernel
    gamma = 1/np.power(gamma, 2)
    #print(rbf_kernel([x ,y] , gamma=gamma), gauss_kernel(x, y, gamma=gamma))
    return rbf_kernel([x, y], gamma=gamma)[0, 1]/\
               (np.power(np.sum(rbf_kernel(np.ones(shape)*x, X, gamma=gamma)[0]), alpha)*
                np.power(np.sum(rbf_kernel(np.ones(shape)*y, X, gamma=gamma)[0]), alpha))


def compute_extension(X, y, eigenvalue, eigenvector, time_step=1, alpha=0.5, gamma=0.4):
    """

    :param X: sample dataset
    :param y: an out-of sample
    :param eigenvalue:
    :param eigenvector:
    :param time_step:
    :param alpha:
    :param gamma:
    :return:
    :argument diffmap_kdij: array
    """
    N, _ = X.shape
    sum = np.zeros(N)
    sum_k_slash = 0
    for x in X:
        sum_k_slash += compute_diffmap_kij_slash(X, x, y, gamma=gamma, alpha=alpha)
    for j in range(N):
        diffmap_kdij = compute_diffmap_kij_slash(X, X[j], y, gamma=gamma, alpha=alpha)/sum_k_slash
        sum[j] = np.sum(eigenvector[j])*diffmap_kdij
    diff_coord = sum / np.power(eigenvalue, time_step)
    return diff_coord

class diff_map():
    def __init__(self, X, gamma=0.8, sample_rate=0.15, time_step=1, alpha=1):
        """

        :param X:
        :param gamma:
        :param sample_rate:
        :param time_step:
        :param alpha: float, controls dependency of the embedding to geometry and density. 0 to both, 1 to geometry only
        """
        self.eigenvalue, self.eigenvector, self.diff_matrix, self.X_S= \
            make_diffusion_map(X, gamma=gamma, sample_rate=sample_rate, time_step=time_step)
        self.X = X
        self.gamma = gamma
        self.time_step = time_step
        self.alpha = alpha
    def diff_map_evaluate(self, k=None):
        """
        Evaluate dataset
        :param k:
        :return:
        """
        scores = np.ones(self.X.shape[0])
        if k is None: k = int(self.X_S.shape[0]/10.0)
        M, _ = self.diff_matrix.shape
        centroid = np.zeros(M)
        covk_matrix = np.zeros((M, M))
        # TODO finish or abort this wrap method

        return
    def diff_map_evaluate_single(self, y, k=None):
        """
        Evaluate one sample
        :param y:
        :param k:
        :return: score of current evaluate, greater means more likely outlier
        """
        if k is None: k = int(self.X_S.shape[0]/10.0)
        M, _ = self.diff_matrix.shape
        centroid = np.zeros(M)
        covk_matrix = np.zeros((M, M))
        # compute diffusion coordinate
        diff_y = compute_extension(self.X_S, y, self.eigenvalue, self.eigenvector,
                                   time_step=self.time_step, alpha=self.alpha, gamma=self.gamma)
        combined = np.concatenate(([diff_y], self.diff_matrix), axis=0)
        # compute score
        nbors = neighbors.kneighbors_graph(X=combined, n_neighbors=k)
        for i, nbor_row in enumerate(nbors):
            inds = nbor_row.indices
            centroid = np.sum(combined[inds], axis=0) / k

            for x in combined[inds]:
                covk_matrix += np.outer(x - centroid, x - centroid)
            break
        _, unit_normal = scipy.linalg.eigh(covk_matrix, eigvals=(0, 0))
        unit_normal = unit_normal[:, 0]
        score = (diff_y - centroid) @ unit_normal
        return score

# End Diffusion Map method