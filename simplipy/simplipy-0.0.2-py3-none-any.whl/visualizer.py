import numpy as np


def corr(df):

    return np.corrcoef(df.T.values)


class Visualizer(object):

    def __init__(self, df, d=corr):

        self.df = df
        self.nodes = df.columns

        self.d = d

    def _compute_distance(self):

        # TODO: Use other similarity measures than correlation here
        self.distances = self.d(self.df)

    def _compute_complex(self):
        pass

    def _get_graph(self):
        pass
