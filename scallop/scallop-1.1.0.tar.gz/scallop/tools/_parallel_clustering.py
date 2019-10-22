import numpy as np
import ray

from ._clustering import do_clustering

@ray.remote
def obtain_btmatrix_col(adj, n_cells, sample_size, empty_value, clustering, *args):
    rnd_idx = np.random.choice(n_cells, size=sample_size, replace=False)

    # We restrict the cells to the ones in rnd_idx
    adj_trial = adj[rnd_idx, :]
    adj_trial = adj_trial[:, rnd_idx]

    arr = np.full(n_cells, empty_value, dtype=int)
    # TODO: arr **kwargs when ray supports them
    arr[rnd_idx] = do_clustering(clustering, adj_trial, *args)
    return arr