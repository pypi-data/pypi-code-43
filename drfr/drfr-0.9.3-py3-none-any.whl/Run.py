import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from src import ReductionModel, BasisGenerator, RegressionModel
#from drfr import ReductionModel, BasisGenerator, RegressionModel
from src.NoveltyDetector import evaluate_novelty
import numpy as np
from sklearn import datasets
import pydiffmap as dm
import warnings
warnings.simplefilter('ignore')





def main():
    N = 5000
    k = 24
    X, color = datasets.samples_generator.make_swiss_roll(n_samples=N, noise=0.01)#
    #X, color = datasets.load_digits(n_class=10, return_X_y=True)
    #X[0] = [30, 30, 30]
    basis_generator = None
    data_name = ""
    poly_degree = 4
    tag_red = "NPPE"
    tag_reg = "lasso"
    red_model = ReductionModel.ReductionModel(n_neighbors=k)
    X, color = red_model.pre_process(X, color, tol_potential=0.8, nov_check=True)
    y_nppe = red_model.get_reduction(X, tag=tag_red)

    reg_model = RegressionModel.RegressionModel()
    y_reg = reg_model.cal_regression(X, y_nppe, normalized=True, tag=tag_reg,
                                     basis_generator=BasisGenerator.generate_kronecker, p=poly_degree)
    print(X.shape)

    potentials = evaluate_novelty(X)

    # illustration of potentials.
    # the x axis has no mathematical implication here
    axis_x = np.linspace(0, 10, num=X.shape[0])

    fig = plt.figure(figsize=(5, 9))

    ax = fig.add_subplot(311)
    ax.scatter(y_nppe[:, 1], y_nppe[:, 0], c=color, cmap=plt.cm.Spectral)
    plt.axis('tight')
    plt.xticks([]), plt.yticks([])
    plt.title('Projected data with ' + tag_red)
    ax = fig.add_subplot(312)
    ax.scatter(y_reg[:, 1], y_reg[:, 0], c=color, cmap=plt.cm.Spectral)
    plt.axis('tight')
    plt.xticks([]), plt.yticks([])
    plt.title("Regressed data with " + tag_reg)
    sub = fig.add_subplot(313)
    sub.scatter(axis_x, potentials, c=color, cmap=plt.cm.Spectral)
    plt.title("The novelty distribution " + tag_reg)
    plt.show()

if __name__ == "__main__":
    # main()
    #X, color = datasets.load_digits(n_class=10, return_X_y=True)
    X, color = datasets.samples_generator.make_swiss_roll(n_samples=5000, noise=0.01)
    # https://pydiffmap.readthedocs.io/en/master/usage.html
    dmap = dm.diffusion_map.DiffusionMap.from_sklearn(n_evecs=1, epsilon=1.0, alpha=0.5, k=24)
    y = dmap.fit_transform(X)
    #potentials = evaluate_novelty(X)

    # illustration of potentials.
    # the x axis has no mathematical implication here
    axis_x = np.linspace(0, 10, num=X.shape[0])
    fig = plt.figure()
    sub = fig.add_subplot(111)
    sub.scatter(y, color, c=color, cmap=plt.cm.Spectral)
    plt.show()
