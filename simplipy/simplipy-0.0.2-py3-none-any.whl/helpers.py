from sklearn.feature_selection.mutual_info_ import _compute_mi
import pandas as pd
import numpy as np


def compute_mutual_information(x, y, x_discrete, y_discrete, n_neighbors=3):
    """
    """

    return _compute_mi(
        x=x,
        y=y,
        x_discrete=x_discrete,
        y_discrete=y_discrete,
        n_neighbors=n_neighbors)


def get_adjacency_matrix(graph):

    df = pd.DataFrame.from_dict(graph.adj)

    for c in df.columns:

        df[c] = df[c].apply(lambda x: x['weight'] if type(x)==dict else np.nan)

    return df
