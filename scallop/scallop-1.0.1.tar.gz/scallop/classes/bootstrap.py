import numpy as np
import pandas as pd
from scipy import stats
import networkx as nx

from . import Scallop
from ..tools._clustering import run_leiden
from ..tools._utils_bt import find_mapping
from ..tools._intersection_functions import return_intersection_function




class Bootstrap():
    """
    Scallop object will store all Bootstraps experiments.

    Parameters
    ----------
    id: ``int``
        ID of `Boostrap` object. This id is useful to retrieve the `Boostrap` object from
        `Scallop.list_bootstraps`.

    scal: :class:`scallop.Scallop`
        `scallop.Scallop` object

    res: ``float``
        Leiden resolution parameter.

    frac_cells: ``float``
        Proportion of cells that will be mapped. It can be in range [0-1].

    n_trials: ``int``
        Number of times bootstrapping will be repeated.
    """

    def __init__(self, id: int,
                 scal: Scallop,
                 res: float,
                 frac_cells: float,
                 n_trials: int):


        self.scal = scal
        self.res = res
        self.frac_cells = frac_cells
        self.n_trials = n_trials
        self.sample_size = int(frac_cells * self.scal.n_cells)
        self.overlap_thresh = 0.1
        self.id = id
        #self.clustering

        self.empty_value = -1
        self.bt_matrix = np.full((self.scal.n_cells, self.n_trials), self.empty_value, dtype=int)
        self.mapped_matrix = None
        self.freq_score = None
        self.most_freq = None
        self.inter_score = None
        self.ident = None
        self.conductance = None

    def _strRepr(self):
        def IDformat(id):
            """
            :param id: Bootstrap ID
            :return: foratted Boostrap ID
            """
            id_str = str(id)
            if len(id_str) == 1:
                id_str = ' ' + id_str
            return id_str

        line = '-'*60 + '\n'
        # string = 'Bootstrap {}:\n- Resolution: {}\n- Fraction of cells:' \
        #          ' {}\n- Number of trials: {}\n'.format(self.id, self.res, self.frac_cells, self.n_trials)
        string = 'Bootstrap ID: {} | res: {} | frac_cells: {} | n_trials: {} '.format(IDformat(self.id), round(float(self.res), 1), self.frac_cells, self.n_trials)
        return line + string

    def __repr__(self):
        return self._strRepr()

    def __str__(self):
        return self._strRepr()

    def _getBtmatrix(self):
        """
        Obtain the bootstrap matrix (self.bt_matrix), that is, a n_cells x n_trials matrix where, in each column, the
        cluster identities with the selected cells are shown. The cells that have not been selected will be filled with
        and exclusion value, or empty value which, by default, is -1.
        """
        # Reference clustering:
        adj = self.scal.annData.uns['neighbors']['connectivities']
        self.ident = run_leiden(adj, res=self.res)
        self.ident_clusters = np.unique(self.ident[self.ident != self.empty_value])

        # Bootstrap iterations:
        for trial in range(self.n_trials):
            rnd_idx = np.random.choice(self.scal.n_cells, size=self.sample_size, replace=False)

            # We restrict the cells to the ones in rnd_idx
            adj_trial = adj[rnd_idx, :]
            adj_trial = adj_trial[:, rnd_idx]

            self.bt_matrix[rnd_idx, trial] = run_leiden(adj_trial, res=self.res)

    def _cluster_mapping_mat(self, bt_col, method='overlap'):
        """
        Given two arrays with the labels of the original clustering, and the bootstrap clustering, returns the matrix
        where each (i,j) element is the score ('overlap', 'jaccard', etc.) between the cells in
        original bootstrap with cluster i, and cells in secondary bootstrap with cluster j.
        """

        bt_ident = self.bt_matrix[:, bt_col]
        clusters_bt = np.unique(bt_ident[bt_ident != self.empty_value])

        n = max(len(self.ident_clusters), len(clusters_bt))
        mapping_matrix = np.zeros((n, n))
        for i in range(len(self.ident_clusters)):
            for j in range(len(clusters_bt)):
                cells_A = set(np.where(self.ident == self.ident_clusters[i])[0])
                cells_B = set(np.where(bt_ident == clusters_bt[j])[0])
                intersection_f = return_intersection_function(method)
                score = intersection_f(cells_A, cells_B)
                mapping_matrix[i][j] = score

        return mapping_matrix, clusters_bt

    def _renameIdent(self, method='overlap'):
        """
        Given the filled self.bt_matrix, obtains a mapping between clusters of different leiden trials.
        The mapping consists of the following steps [for each column on self.bt:matrix]:
        1) Obtain the column
        2) Call cluster_mapping_mat(), which will return the matrix of mapping between clusters of reference and
           bootstrap columns. This is a n_clusters_ref x n_clusters_bt matrix for which the cell i,j is a score
           (e.g., jaccard index) of the cell overlap between the cluster i of the reference and the cluster j of the bt
           matrix. The higher the value the greater the overlap, and the higher the chance that cluster j should be
           renamed as i.
        3) Obtain the permutation of clusters from bootstrap that maximizes the similarity of clusters, that is, that
           optimizes the trace of the mapping matrix.
        4)

        Parameters
        ----------
        method: str
            Method of intersection score between two sets ('bool', 'overlap', 'jaccard', 'max', 'min').

        Returns
        -------
        None
        """
        #Todo: solve issue when freq(most freq) == freq(second most freq)
        self.mapped_matrix = np.full((self.scal.n_cells, self.n_trials), self.empty_value)
        clusters_ident = np.unique(self.ident[self.ident != self.empty_value])
        unk_count = len(clusters_ident)

        for bt_trial in range(self.n_trials):
            mapping_matrix, clusters_bt_trial = self._cluster_mapping_mat(bt_col=bt_trial, method=method)

            perm = find_mapping(mapping_matrix)

            mapped_diag = mapping_matrix[:, [item[1] for item in perm]].diagonal()
            nonzero = np.argwhere(mapped_diag > self.overlap_thresh).ravel()
            nonzero_perm = [perm[i] for i in nonzero]
            zero_perm = [perm[i] for i in np.argwhere(mapped_diag <= self.overlap_thresh).ravel()]

            clusters_perm = {clusters_bt_trial[i[1]]: clusters_ident[i[0]] for i in nonzero_perm}
            for i in zero_perm:
                if i[1] in clusters_bt_trial:
                    clusters_perm[clusters_bt_trial[i[1]]] = unk_count
                    unk_count += 1

            for c in list(clusters_perm.keys()):
                self.mapped_matrix[np.argwhere(self.bt_matrix[:,bt_trial] == c).ravel(), bt_trial] = clusters_perm[c]


    def _freqScore(self, do_return=False):
        print('Doing Freq Score')
        """
        Obtains the frequency score for the sample, that is, the frequency of the most frequently assigned cluster
        identity per cell is stored in annData.obs['freq'].

        Parameters
        ----------
        do_return: bool
        If True, returns the freqScore pandas series.

        Returns
        -------
        return: pandas.Series
        Series object with freq score for each cell.
        """
        mode, count = stats.mode(self.mapped_matrix, axis=1)
        self.most_freq = mode.ravel()
        self.freq_score = count.ravel()/self.n_trials
        if do_return:
            return pd.DataFrame(self.freq_score,
                                index=self.scal.annData.obs_names, columns=['freqScore'])

    def _interScore(self):
        print('Doing Inter Score')
        pass
