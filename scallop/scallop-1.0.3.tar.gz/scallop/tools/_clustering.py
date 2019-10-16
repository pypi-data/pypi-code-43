import leidenalg
from scanpy.utils import get_igraph_from_adjacency
import numpy as np

def run_leiden(adj, res):
    g = get_igraph_from_adjacency(adj, directed=True)
    part = leidenalg.find_partition(g, leidenalg.RBConfigurationVertexPartition, resolution_parameter=res)
    groups = np.array(part.membership)
    # print('DONE Leiden with res {res}'.format(res=res), 'Length of groups:', len(groups))
    return groups