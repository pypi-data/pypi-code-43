import numpy as np
import scipy
from sklearn import neighbors
from itertools import chain, combinations_with_replacement
import umap
from sklearn.neighbors import NearestNeighbors
from sklearn.manifold import LocallyLinearEmbedding, SpectralEmbedding, TSNE, Isomap
from sklearn.decomposition import PCA, KernelPCA
import pydiffmap as dm
import NoveltyDetector as nd
import pydiffmap as dm

class ReductionModel():
    def __init__(self, kronecker_degree = 3, n_neighbors = 24, n_components = 2, scraber = None):
        """

        :param kronecker_degree: int
        :param n_neighbors: int
        :param n_components: int
        :param scraber: the outlier identifier to be used
        """
        self.kronecker_degree = kronecker_degree
        self.k = n_neighbors
        self.n = n_components
        self.funcs = [self.fit_transform, umap.UMAP(n_neighbors=n_neighbors).fit_transform,
                 LocallyLinearEmbedding(n_components=n_components,
                                        n_neighbors=n_neighbors, method="modified").fit_transform,
                 LocallyLinearEmbedding(n_components=n_components, n_neighbors=n_neighbors, method="hessian",
                                        eigen_solver="dense").fit_transform,
                 SpectralEmbedding(n_components=n_components).fit_transform,
                 TSNE(n_components=n_components).fit_transform,
                 Isomap(n_components=n_components).fit_transform
                 ]
        self.labels = ["NPPE", "UMAP", "LLE", "Hessian", "Spectral", "TSNE", "Isomap"]

    # for kronecker computation
    def p(self, a):
        """
        A help function to compute kronecker multiplication

        :param a: array-like N*n
        :return:
        """
        (N,) = a.shape  # Unpacking fails if a is not 1-dimensional
        index_combs = chain.from_iterable((
            combinations_with_replacement(range(N), r) for r in range(1, self.kronecker_degree)))
        return [np.prod(a[list(indices)]) for indices in index_combs]

    def compute_kronecker(self, X):
        """

        :param X: array-like N*n
        :return: array-like N*(n*n)
        """
        return np.apply_along_axis(self.p, 1, X)

    def compute_hadamard(self, X):
        """

        :param X: array-like N*n
        :return: array-like N*(n*kronecker_degree)
        """
        x_hadamard = []
        N, _ = X.shape
        for i in range(N):
            x_hadamard_i = []
            # counting from kronecker_degree to 1
            for t in reversed(range(self.kronecker_degree+1)):
                if (t != 0):
                    # hadamard product of each X^i_p
                    x_hadamard_i = np.concatenate((x_hadamard_i, np.power(X[i], t)), axis=None)
            x_hadamard.append(x_hadamard_i)
        x_hadamard = np.array(x_hadamard)
        return x_hadamard

    def compute_w(self, X):
        """

        :param X:  array-like N*n matrix
        :return: array-like N*N matrix, the Neighborhood weight matrix of NPPE
        """
        N, _ = X.shape
        nbors = neighbors.kneighbors_graph(X, n_neighbors=self.k)
        W = np.zeros((N, N))
        for i, nbor_row in enumerate(nbors):
            # Get the indices of the nonzero entries in each row of the
            # neighbors matrix (which is sparse). These are the nearest
            # neighbors to the point in question. dim(Z) = [K, D]
            inds = nbor_row.indices
            Z = X[inds] - X[i]

            # Local covariance. Regularize because our data is
            # low-dimensional (K > D). dim(C) = [K, K]
            C = np.float64(np.dot(Z, Z.T))
            C += np.eye(self.k) * np.trace(C) * 0.001

            # Compute reconstruction weights
            w = scipy.linalg.solve(C, np.ones(self.k))
            W[i, inds] = w / sum(w)
        return W

    def fit_transform(self, X, offset=False, simple=True):
        """
        The fit_transform function for NPPE.

        :param X: array-like N*n matrix
        :param offset: boolean, default as False. By True the basis data matrix would be added by\
        some random value, to avoid singularity, which is achieved elsewhere, so this argument maybe redundant.

        :param simple: boolean, True=hadamard basis; False=Kronecker basis
        :return: array-like N*m matrix, the embedded data matrix

        """
        # compute diagonal D based on row sum of W
        N, n = X.shape
        W = self.compute_w(X)

        if simple:
            P = self.compute_hadamard(X)
        else:
            P = self.compute_kronecker(X)
        if offset:
            P_offset = P + np.random.rand(P.shape[0], P.shape[1])
        else:
            P_offset = P
        D = np.zeros((N, N))
        np.fill_diagonal(D, W.sum(axis=1))
        # Create sparse, symmetric matrix
        M = np.dot((D - W).T, (D - W))
        M = M.T
        A = np.dot(np.dot(P_offset.T, M), P_offset)  # X_p(D-W)X_p.T in the paper
        B = np.dot(np.dot(P_offset.T, D), P_offset)  # X_pDX_p.T in the paper
        # in case A or B is singular
        if scipy.linalg.det(A) == 0 or scipy.linalg.det(B) == 0:
            pca = PCA(n_components=min(30, n-1))
            X_pca = pca.fit_transform(X)
            return self.fit_transform(X_pca)
        vals, vecs = scipy.linalg.eigh(A, B, eigvals=(0, self.n-1))
        y = np.dot(P_offset, vecs)
        return y

    def get_reduction(self, X, cal_all = False, tag = "NPPE"):
        """
        :param X: array-like N*n
        :param cal_all: boolean, if True, return an array containing results of all given Reduction methods
        :param tag: string
        :return: y is either one reduced data-set or an array of them, according to cal_all
        """
        y = None
        if not cal_all:
            if tag == "NPPE": y = self.fit_transform(X)
            elif tag == "UMAP": y = umap.UMAP(n_neighbors=self.k).fit_transform(X)
            elif tag == "LLE" : y = LocallyLinearEmbedding(n_components=self.n,
                                            n_neighbors=self.k, method="modified").fit_transform(X)
            elif tag == "Hessian": y = LocallyLinearEmbedding(n_components=self.n,
                                                                   n_neighbors=self.k, method="hessian",
                                            eigen_solver="dense").fit_transform(X)
            elif tag == "Spectral": y = SpectralEmbedding(n_components=self.n).fit_transform(X)
            elif tag == "TSNE" : y = TSNE(n_components=self.n).fit_transform(X)
            elif tag == "Isomap": y = Isomap(n_components=self.n).fit_transform(X)
        else:
            y = []
            for f, label in zip(self.funcs, self.labels):
                y.append(f(X))
        return y

    def fast_outlier_iden_step1(self, X, tol=1e-2, max_iter=1000):
        """
        The fast outlier identifying algorithm according to section 4.2 in paper Robust Hessian LLE.
        Following implements the first step of 4.2.

        :param X: array-like N*n matrix
        :param tol: float
        :param max_iter: int
        :return: (N*N, N*n), the array-like N*N weight matrix indicating outliers, and\
        the N*n matrix, the mean coordinate of k Nearest Neighbors of each x_i in X.

        """
        N, _ = X.shape
        nbrs = NearestNeighbors(n_neighbors=self.k + 1, algorithm='ball_tree').fit(X)
        distances, indices = nbrs.kneighbors(X)
        # w^i_j, sigma, x^ in paper Robust Hessian LLE
        w_outlier = np.zeros((N, N))
        sigmas = np.mean(distances[:, 1:], axis=1) ** 2
        x_knn_mean = np.mean(X[indices[:, 1:]], axis=1)

        checked = np.zeros(N, dtype=bool)
        loop = 0
        while loop <= max_iter:
            x_knn_mean_new = np.zeros(x_knn_mean.shape)
            # the denominator
            bot_sum = np.zeros(N)
            for i in range(N):
                for j in indices[i, 1:]:
                    bot_sum[i] += np.exp(-np.linalg.norm(X[j] - x_knn_mean[i]) ** 2 / sigmas[i])
            # the numerator
            for i in range(N):
                # ignore already fitted sample
                if checked[i]: continue
                for j in indices[i, 1:]:
                    w_outlier[i, j] = np.exp(-np.linalg.norm(X[j] - x_knn_mean[i]) ** 2 / sigmas[i]) / bot_sum[i]
                    x_knn_mean_new[i] += w_outlier[i, j] * X[j]
                if np.linalg.norm(x_knn_mean_new[i] - x_knn_mean[i]) < tol:
                    checked[i] = True
                    continue
                x_knn_mean[i] = x_knn_mean_new[i]
            if np.all(checked):
                #print("identify loops:", loop)
                return w_outlier
            loop += 1
        #print("identify loops:", loop)
        return (w_outlier, x_knn_mean)


    def pre_process(self, X, color, alpha=0.2, tol=1e-2, tol_potential=0.5,
                    max_iter=1000, nov_check=False, diffmap=False):
        """
        :param X: N*n, input data
        :param color: N dimensional array, input labels
        :param alpha: float, the threshold
        :param tol: float, parameter for the identifier algorithm
        :param max_iter: int, parameter for the identifier algorithm
        :return: data set with recognized outliers removed

        """
        w_outlier = self.fast_outlier_iden_step1(X, tol=tol, max_iter=max_iter)
        score = np.sum(w_outlier, axis=0)
        outlier_indices = np.argwhere(score < alpha)
        X_rem = np.delete(X, outlier_indices, axis=0)
        color_rem = np.delete(color, outlier_indices, axis=0)
        if nov_check:
            potentials = nd.evaluate_novelty(X=X)
            novelty_indices = np.argwhere(potentials < tol_potential*potentials.min())
            X_rem = np.delete(X_rem, novelty_indices, axis=0)
            color_rem = np.delete(color_rem, novelty_indices, axis=0)


        return (X_rem, color_rem)