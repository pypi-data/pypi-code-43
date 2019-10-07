from sklearn.metrics.pairwise import rbf_kernel
import numpy as np
import scipy
from scipy.spatial.distance import euclidean as euc
import random
from DiffusionMap import diff_map
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt

def compute_kij_slash(X, gamma=0.4):
    """
    compute the k_ij_slash matrix according to H.Hoffman Eq.4
    :param X: array-like (N,n)
    :argument
    :return k_ij_slash: array-like (N,N)
    """
    N,_ = X.shape
    k_ij_matrix = rbf_kernel(X, gamma=gamma)
    k_ir_vec = np.sum(k_ij_matrix, axis=0)/N
    k_rs = np.sum(k_ij_matrix, axis=None)/(N**2)
    k_ij_slash = np.zeros((N, N))
    # for i in range(N):
    #     for j in range(N):
    #         k_ij_slash[i, j] = k_ij_matrix[i, j] - k_ir_vec[i] - k_ir_vec[j] + k_rs
    i, j = np.meshgrid(k_ir_vec, k_ir_vec)
    k_ij_slash = k_ij_matrix - i - j + k_rs
    return k_ij_slash

def compute_projection(X, current_x_id, alphas=None, k_ij_slash=None,
                       current_component=1):
    """
    compute the projection according to Eq.9 in Hoffman's paper.
    Projection: from hyper-high dimensional to n_component-dimensional, as potential
    :param X: (N,n)
    :param current_x_id: int
    :param current_component: int, ranged from 1 to n_principal_component
    :argument
    :return projection: float
    """
    N,_ = X.shape

    # main computation
    projection = 0
    for i in range(N):
        projection += alphas[current_component-1, i]*k_ij_slash[current_x_id, i]
    return projection

def compute_sphere_potential(X):
    """
    compute potential of data X[current_x] according to Eq.7 in Hoffman's paper
    :param X: (N,n)
    :return potentials: (N,)
    """
    N, _ = X.shape
    k_ij_matrix = rbf_kernel(X)
    potentials = -np.sum(k_ij_matrix, axis=0)*2/N
    return potentials


from scipy.special import softmax


def draw_roc(y_test=None, y_score=None, n_classes=2):
    """
    y_test: true outliers labels array
    y_score: predicted outliers labels array in score form
    """
    # transform score to probability
    # y_score = softmax(y_score)
    fpr, tpr, _ = roc_curve(y_test, y_score)
    roc_auc = auc(fpr, tpr)

    # Compute micro-average ROC curve and ROC area
    # fpr["micro"], tpr["micro"], _ = roc_curve(y_test.ravel(), y_score.ravel())
    # roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

    plt.figure()
    lw = 2
    plt.plot(fpr, tpr, color='darkorange',
             lw=lw, label='ROC curve (area = %0.2f)' % roc_auc)
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.show()

def k_pca_evaluate(X, n_principal_component=20, gamma=0.6):
    """

    :param X:
    :param n_principal_component:
    :param gamma:
    :return:
    """
    N, _ = X.shape
    projections = np.zeros((N,))

    k_ij_slash = compute_kij_slash(X, gamma=gamma)

    # get greatest eigenvalues and vectors according to n_principal_component
    eigenvalue, alphas = scipy.linalg.eigh(k_ij_slash)
    indices = eigenvalue.argsort()[-n_principal_component:][::-1]
    # eigenvalue = eigenvalue[indices]
    alphas = alphas[indices]
    for k in range(N):
        projection = 0
        for i in range(n_principal_component):
            projection += compute_projection(X, k, alphas=alphas, k_ij_slash=k_ij_slash,
                                             current_component=i + 1) ** 2
        projections[k] = projection
    potentials = projections - compute_sphere_potential(X)
    return potentials

def evaluate_novelty(X, n_neighbors = None, n_principal_component=20, gamma=0.6, method="kpca",
                     sample_rate=0.15, time_step=1, alpha=1):
    """
    compute scores for all data in X. X with larger ABSOLUTE values are likely to be
    novelties.
    :param X: (N,n)
    :param n_principal_component: int, not larger than N
    :param gamma:
    :param alpha: float, [0, 1] to 0--density sensitive; to 1--geometry sensitive
    :return scores: (N,)
    """
    scores = None
    if method == "kpca":
        scores = k_pca_evaluate(X, n_principal_component=n_principal_component, gamma=gamma)
    elif method == "dmap":
        dm = diff_map(X, gamma=gamma, sample_rate=sample_rate, time_step=time_step, alpha=alpha)
        scores = np.ones(X.shape[0])

        i = 0
        for x in X:
            scores[i] = dm.diff_map_evaluate_single(x, k=n_neighbors)
            i += 1
    return scores