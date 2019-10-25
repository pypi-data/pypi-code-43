from typing import Any, Mapping

import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt

from .utils import add_identity


def annotate_correlation(
    x: pd.Series, y: pd.Series,
    method: str,
    **kwargs: Any
) -> None:
    """Plot correlation.

    Adapted from https://github.com/mwaskom/seaborn/issues/1444
    """
    # compute correlation
    corr_r = x.corr(y, method)
    corr_text = f'{corr_r:2.2f}'.replace('0.', '.')

    # visualize correlation
    ax = plt.gca()
    ax.set_axis_off()

    marker_size = abs(corr_r) * 10000
    ax.scatter(
        .5, .5, marker_size, corr_r, alpha=0.6,
        cmap='vlag_r', vmin=-1, vmax=1,  # bwr_r
        transform=ax.transAxes)

    ax.annotate(
        corr_text,
        [.5, .5], xycoords='axes fraction',
        ha='center', va='center', fontsize=20)


def custom_distplot(x, **kwargs):
    """Automatically remove NaN values."""
    sns.distplot(pd.Series(x).dropna(), **kwargs)
    # print(pd.Series(x).dropna())
    # sns.distplot(pd.Series(x).dropna(), **kwargs)
    # plt.hist(x, **kwargs)


def custom_scatterplot(*args, **kwargs):
    """Enhance default scatterplot with identity line."""
    ax = sns.scatterplot(*args, **kwargs)  # regplot
    add_identity(ax, color='grey', ls='--', alpha=.5)


def corrplot(
    df: pd.DataFrame,
    corr_method: str = 'spearman',
    upper_kws: Mapping[str, Any] = None,
    diag_kws: Mapping[str, Any] = None,
    lower_kws: Mapping[str, Any] = None,
    **kwargs: Any
) -> sns.PairGrid:
    """Implement an improved version of `sns.pairplot`."""
    # setup
    upper_kws = upper_kws or {}
    diag_kws = diag_kws or {}
    lower_kws = lower_kws or {}

    # plotting
    g = sns.PairGrid(df, **kwargs)

    g.map_upper(annotate_correlation, method=corr_method, **upper_kws)
    g.map_diag(custom_distplot, **diag_kws)
    g.map_lower(custom_scatterplot, **lower_kws)

    return g


if __name__ == '__main__':
    import numpy as np
    import pandas as pd

    # generate data
    np.random.seed(1)

    N = 200
    xs = np.sort(np.random.normal(size=N))

    df = pd.DataFrame({
        'A': xs,
        'B': np.random.normal(size=N),
        'C': xs + np.random.normal(0.01, size=N),
        'D': xs[::-1] + np.random.normal(0.01, size=N)
    })
    print(df.head())

    # plot
    corrplot(df)
    plt.show()
