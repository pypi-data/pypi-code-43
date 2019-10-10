import matplotlib.pyplot as plt
import numpy as np
from typing import List, Union

from .result import FullResult, ArrayResult


def plot(
        result: Union[FullResult, ArrayResult],
        x_indices: List[int] = None,
        x_names: List[str] = None,
        show_mean: bool = True,
        show_std: bool = True,
        set_xlim_to_t_max: bool = True,
        show_legend: bool = True,
        show: bool = False,
        ax = None):
    # generate matrix
    if isinstance(result, FullResult):
        result = result.for_timepoints()

    # dimensions
    nr, nt, nx = result.matrix_xs.shape

    # species to plot
    if x_indices is None:
        x_indices = list(range(nx))
    n_indices = len(x_indices)

    # labels
    if x_names is None:
        x_names = ["x" + str(ix) for ix in x_indices]

    # need a color
    cm = plt.get_cmap()

    # plot
    if ax is None:
        _, ax = plt.subplots()

    for ix in range(n_indices):
        for ir in range(nr):
            ax.step(result.ts,
                    result.matrix_xs[ir, :, x_indices[ix]],
                    color=cm(ix / n_indices),
                    alpha=nr**-0.8,
                    label=x_names[ix])
    
    # limits
    if set_xlim_to_t_max:
        ax.set_xlim([0, result.t_max])

    # legend
    legend = ([plt.Line2D([0], [0], color=cm(ix / n_indices)) for ix in range(n_indices)], x_names)

    # mean
    mean = np.mean(result.matrix_xs, axis=0)
    if show_mean and nr > 1:
        for ix in range(n_indices):
            ax.step(
                result.ts,
                mean[:, ix],
                alpha=1.0,
                color=cm(ix / n_indices),
                label="mean")
            #legend[0].append(plt.Line2D([0], [0], color=cm(ix / n_indices), alpha=1.0))
            #legend[1].append("mean " + x_names[ix])

    if show_std and nr > 1:
        std = np.sqrt(np.var(result.matrix_xs, axis=0))
        for ix in range(n_indices):
            ax.fill_between(
                result.ts,
                mean[:, ix] - std[:, ix], mean[:, ix] + std[:, ix],
                color=cm(ix / n_indices),
                alpha=nr**-0.8)

    # add legend
    if show_legend:
        ax.legend(*legend)

    # show on screen
    if show:
        plt.show()

    return ax
