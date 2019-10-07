from sklearn import datasets, neighbors, linear_model, cluster
from scipy.special import *
from pyearth import Earth
class RegressionModel():
    def __init__(self):

        return

    def cal_regression(self, X, y,
                       tag = "lasso", normalized = True, alpha = 0.001, basis_generator = None, p=4):
        """

        :param X: array-like N*n matrix, original data
        :param y: array-like N*m matrix, embedded lower dimensional data
        :param basis_generator: a basis generator function. For implemented basis functions, check BasisGenerator.py
        :param p: int, polynomial degree of basis
        :param tag: string
        :return: the lower dimensional data computed by the derived regression coefficient given X and y
        """
        N, n = X.shape
        if normalized:
            x_max = np.max(X, axis=0)
            coef = np.linalg.norm(x_max)
            X = X/coef
            alpha = alpha/coef
        lasso = linear_model.Lasso(alpha=alpha, max_iter=1000)
        ridge = linear_model.Ridge(alpha=alpha, max_iter=1000)
        y_reg = y
        if basis_generator == None:
            print("a valid basis generator needed!")
            return

        #if basis_generator == BasisGenerator.generate_spline:
        basis = basis_generator(X, y, p=p)
        if tag == "lasso":
            lasso.fit(basis, y)
            y_reg = np.dot(basis, lasso.coef_.T)
        elif tag == "ridge":
            ridge.fit(basis, y)
            y_reg = np.dot(basis, ridge.coef_.T)
        elif tag == "MARS":
            #model = Earth(max_degree=2, minspan_alpha=.5, verbose=False)
            model = Earth()
            model.fit(X, y)
            y_reg = model.predict(X)

        return y_reg

