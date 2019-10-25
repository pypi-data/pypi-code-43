from typing import Tuple, Dict

import numpy as np
import pandas as pd
import pandas.api.types as ptypes
import networkx as nx

from gene_map import GeneMapper


def _get_stringdb_to_entrez_map(
    fname: str = 'data/9606.protein.aliases.v10.5.txt.gz'
) -> Dict[str, str]:
    """ Map StringDB to Entrez using custom Ensembl ids
    """
    # read custom StringDB-Ensembl mapping
    df_map = pd.read_table(
        'data/9606.protein.aliases.v10.5.txt.gz', skiprows=1,
        header=None, names=['string_protein_id', 'alias', 'source'])
    df_map_ens = df_map[df_map['source'] == 'Ensembl'].dropna()

    df_map_str2ens = df_map_ens[['string_protein_id', 'alias']]
    df_map_str2ens.columns = ('stringdb', 'ensembl')

    # convert Ensembl to Entrez
    gm = GeneMapper()
    id_list = list(set(df_map_str2ens['ensembl'].tolist()))
    gm_res = gm.query(id_list, source_id_type='auto', target_id_type='GeneID')

    # merge results
    df_mapping = df_map_str2ens.merge(
        gm_res,
        left_on='ensembl', right_on='ID_from',
        how='left'
    ).drop('ID_from', axis=1).rename(columns={'ID_to': 'entrez'}).dropna()
    gene_id_map = df_mapping.set_index('stringdb').to_dict()['entrez']

    return gene_id_map


def load_stringdb(
    fname: str = 'data/9606.protein.links.v10.5.txt.gz',
    threshold: int = 850
) -> Tuple[nx.Graph, pd.DataFrame]:
    """ Load protein-interaction data from StringDB
        and convert entries to ENTREZ ids
    """
    df = pd.read_table(fname, sep=' ')
    df_sub = df[df['combined_score'] >= threshold].copy()

    id_map = _get_stringdb_to_entrez_map()
    df_sub['protein1'] = df_sub['protein1'].apply(
        lambda x: id_map.get(x, np.nan))
    df_sub['protein2'] = df_sub['protein2'].apply(
        lambda x: id_map.get(x, np.nan))
    df_sub.dropna(inplace=True)

    assert ptypes.is_string_dtype(df_sub['protein1'])
    assert ptypes.is_string_dtype(df_sub['protein1'])

    graph_all = nx.convert_matrix.from_pandas_edgelist(
        df_sub,
        source='protein1', target='protein2',
        edge_attr='combined_score')
    graph = max(nx.connected_component_subgraphs(graph_all), key=len)

    return graph, df_sub
