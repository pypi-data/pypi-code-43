import os
import itertools

import networkx as nx

from tqdm import tqdm_notebook as tqdm
from bs4 import BeautifulSoup


def load_kegg_graph(xml):
    """ Load single KEGG pathway as networkx graph
    """
    soup = BeautifulSoup(xml, 'lxml')

    # retrieve nodes
    node_data = {}
    for gene in soup.pathway.find_all('entry', type='gene'):  # add genes
        g_idx = str(gene['id'])
        g_entrez = [str(g.lstrip('hsa:')) for g in gene['name'].split()]

        assert g_idx not in node_data
        node_data[g_idx] = g_entrez
    actual_genes = dict(node_data)

    for group in soup.pathway.find_all('entry', type='group'):  # add groups
        g_idx = str(group['id'])
        c_idx = [str(c['id']) for c in group.find_all('component')]

        assert g_idx not in node_data
        for i in c_idx:
            assert i in node_data

        node_data[g_idx] = [g for c in c_idx for g in node_data[c]]

    # retrieve links
    link_data = []
    # add self-links for kegg-ids with
    # multiple associated ENTREZ ids
    for idx, names in actual_genes.items():
        link_data.extend(itertools.combinations(names, 2))

    for intact in soup.pathway.find_all('relation'):
        source = str(intact['entry1'])
        target = str(intact['entry2'])

        if source in node_data and target in node_data:
            link_data.extend(
                itertools.product(
                    node_data[source], node_data[target]))

    # assemble graph
    g = nx.Graph(
        name=f'{soup.pathway["title"]}, {soup.pathway["name"][5:]}',
        title=soup.pathway['title'], id=soup.pathway['name'][5:])
    g.add_nodes_from(
        [(g, {'kegg_id': i})
         for i, gl in actual_genes.items() for g in gl])
    g.add_edges_from(link_data)

    return soup.pathway['name'].split(':')[1], g


def load_kegg_database(data_dir='./data/kegg'):
    """ Load all given KEGG data
    """
    kegg_data = {}
    for pathway_entry in tqdm(
        os.scandir(data_dir),
        total=len(os.listdir(data_dir))
    ):
        with open(pathway_entry.path) as fd:
            name, graph = load_kegg_graph(fd.read())

        assert name not in kegg_data
        kegg_data[name] = graph
    return kegg_data
