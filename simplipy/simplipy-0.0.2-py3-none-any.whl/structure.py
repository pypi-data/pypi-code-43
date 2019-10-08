from simplipy.helpers import compute_mutual_information
from itertools import combinations
import networkx as nx


class Structure(object):

    def visualie(self):
        raise NotImplementedError()

    def compute(self, df):
        self.learn(df)

    def learn(self, df):
        raise NotImplementedError()


class Complex(Structure):

    pass


class Graph(Structure):
    def _setup_graph(self, df):
        G = nx.Graph()

        for c in df.columns:
            G.add_node(c)

        return G

    def visualize(self):

        # TODO: Visualize with multidimensional scaling

        pass


class BayesianNetwork(Graph):

    def learn(self, df):
        graph = self._setup_graph(df)

        for x, y in combinations(df.columns, 2):
            mi = compute_mutual_information(
                x=df[x],
                y=df[y],
                x_discrete=True,
                y_discrete=True
            )

            # Add the negativ mutual information because later, we compute a minimum spanning tree
            graph.add_edge(
                u=x,
                v=y,
                weight=-mi)

        self.graph = nx.minimum_spanning_tree(graph)
