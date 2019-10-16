import logging

from ..classes.scallop import Scallop
from ..classes.bootstrap import Bootstrap
import pandas as pd
import matplotlib.axes as ax


def getScore(scal: Scallop,
             res: [float, int] = 0.3,
             frac_cells: float = 0.95,
             n_trials: int = 25,
             score_type: str = "freq",
             do_return: bool = False):
    """
    Obtains the score for each cell given resolution, clustering and the rest of parameters.

    Parameters
    ----------
    scal : :class:`Scallop`
        Scallop object

    res : ``int``,  ``float``
        Leiden resolution parameter.

    frac_cells : ``float``
        Proportion of cells that will be mapped. It can be in range [0-1].

    n_trials : ``int``
        Number of times bootstrapping will be repeated.

    score_type : ``str``
        Score type. Currently, only 'freq' is supported.

    do_return : ``bool``
        Return score as a ``pandas.Series`` object.

    Returns
    -------
    score : :class:`pandas.Series`
        Object with score per cell, and the names of cells as index.
    """

    # We will first check if a Bootstrap object with the required parameters already exists.
    # If so, it will not generate a new Bootstrap object. Else, it appends a new Bootstrap
    # object to the Scallop object
    print('Res: %s | frac_cells: %s | n_trials: %s | score_type: %s' %(res, frac_cells, n_trials, score_type))

    exists_bootstrap = False

    for idx in range(len(scal.list_bootstraps)):

        # Check whether a BT object exists with the same parameter values:
        if (scal.list_bootstraps[idx].res == res) and (scal.list_bootstraps[idx].frac_cells == frac_cells) \
            and (scal.list_bootstraps[idx].n_trials == n_trials):

            exists_bootstrap = True
            print('A Bootstrap object with these parameter values already existed')
            bootstrap_obj = scal.list_bootstraps[idx]
            if do_return:
                return pd.DataFrame(scal.list_bootstraps[idx].freq_score, index=scal.annData.obs_names, columns=['freqScore'])
            break

    if not exists_bootstrap:
        idx = len(scal.list_bootstraps)
        # Because if the bootstrap does not exist, its ID will be equal to the length of list_bootstraps, as
        # the new botstrap will be added to the queue
        bootstrap_obj = Bootstrap(id=len(scal.list_bootstraps), scal=scal, res=res, frac_cells=frac_cells, n_trials=n_trials)
        scal.list_bootstraps.append(bootstrap_obj)
        print('The Bootstrap object did not exist and has been created.')

        bootstrap_obj._getBtmatrix()

    if score_type == 'freq':
        if bootstrap_obj.mapped_matrix is None:
            bootstrap_obj._renameIdent()

        if bootstrap_obj.freq_score is None:
            bootstrap_obj._freqScore()

    elif score_type == 'inter':
        if bootstrap_obj.inter_score is None:
            bootstrap_obj._interScore()
    else:
        raise AttributeError('The score type can be "freq" or "inter".')

    if do_return:
        return pd.DataFrame(scal.list_bootstraps[idx].freq_score, index=scal.annData.obs_names, columns=['freqScore'])


def plotScore(scal: Scallop,
              score_type: str = "freq",
              plt_type: str = 'umap',
              bt_id: int = None,
              ax: ax.Axes = None,
              show: bool = True):
    """
    Plots the score from ``sl.tl.getScore()``

    Parameters
    ----------
    scal : :class:`Scallop`
        Scallop object

    score_type : ``str``
        Score type. Currently, only 'freq' is supported.

    plt_type : ``str``
        Plot type ("umap", "tsne", "phate", "pca").

    bt_id : ``int``
        Bootstrap id from scal.bootstrap_list. Run ``scal.getAllBootstraps()`` to see the
        id associated to certain conditions.

    ax : :class:`matplotlib.axes.Axes`
        Axis object in which store the plot.

    show : ``bool``
        Shows the plot on window.

    Returns
    -------
    ax : :class:`matplotlib.axes.Axes`
        Stores the score axes into ``ax``.
    """

    scal._plotScore(score_type=score_type, plt_type=plt_type, bt_id=bt_id, ax=ax, show=show)
