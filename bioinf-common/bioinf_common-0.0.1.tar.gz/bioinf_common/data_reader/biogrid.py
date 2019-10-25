from typing import Tuple

import pandas as pd
import pandas.api.types as ptypes
import networkx as nx


def load_biogrid(
    fname: str = 'data/BIOGRID-ORGANISM-Homo_sapiens-3.4.153.tab2.txt'
) -> Tuple[nx.Graph, pd.DataFrame]:
    """ Load protein-interaction data from BioGRID
    """
    # BioGRID
    df_bgrid = pd.read_table(fname, low_memory=False)

    # subset physical interactions
    df_bgrid_phys = df_bgrid[
        df_bgrid['Experimental System Type'] == 'physical'].copy()

    df_bgrid_phys['Entrez Gene Interactor A'] = df_bgrid_phys[
        'Entrez Gene Interactor A'].astype(str)
    df_bgrid_phys['Entrez Gene Interactor B'] = df_bgrid_phys[
        'Entrez Gene Interactor B'].astype(str)

    assert ptypes.is_string_dtype(df_bgrid_phys['Entrez Gene Interactor A'])
    assert ptypes.is_string_dtype(df_bgrid_phys['Entrez Gene Interactor B'])

    # create network
    graph_bgrid_all = nx.convert_matrix.from_pandas_edgelist(
        df_bgrid_phys,
        source='Entrez Gene Interactor A', target='Entrez Gene Interactor B',
        edge_attr='Score')

    subgraphs = nx.connected_component_subgraphs(graph_bgrid_all)
    graph_bgrid = max(subgraphs, key=len)

    return graph_bgrid, df_bgrid_phys
