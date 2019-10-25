import sys

from typing import Dict, Set

import obonet
import pandas as pd

from gene_map import GeneMapper

from tqdm import tqdm


def load_goterms(
    data_dir: str = 'data/',
    nested: bool = False, prune_steps: int = 0
) -> Dict[str, Set[str]]:
    """ Load Gene-Ontology terms from:
         * GO-network:
            http://purl.obolibrary.org/obo/go.obo
         * GO-gene associations:
            ftp://ftp.ebi.ac.uk
            /pub/databases/GO/goa/HUMAN/goa_human.gaf.gz

        If `nested`, recursively assemble GO-categories
    """
    # read data
    df = pd.read_table(
        f'{data_dir}/goa_human.gaf.gz',
        comment='!', header=None, low_memory=False,
        names=[
            'DB', 'DB Object ID', 'DB Object Symbol', 'Qualifier', 'GO ID',
            'DB:Reference (|DB:Reference)', 'Evidence Code', 'With (or) From',
            'Aspect', 'DB Object Name', 'DB Object Synonym (|Synonym)',
            'DB Object Type', 'Taxon(|taxon)', 'Date', 'Assigned By',
            'Annotation Extension', 'Gene Product Form ID'])

    # translate gene IDs
    df = df[df['DB'] == 'UniProtKB']

    gm = GeneMapper()
    res = gm.query(
        df['DB Object ID'].tolist(),
        source_id_type='ACC', target_id_type='GeneID')

    df = df.merge(res, left_on='DB Object ID', right_on='ID_from')
    df.rename(columns={'ID_to': 'GeneID'}, inplace=True)

    # assemble raw associations (non-inclusive)
    raw_associations = {}
    sub = df[['GO ID', 'GeneID']]
    for term, group in tqdm(sub.groupby('GO ID')):
        genes = set(group['GeneID'].tolist())
        raw_associations[term] = genes

    if nested:
        # read GO-network
        go_net = obonet.read_obo(f'{data_dir}/go.obo')

        # connect main GO-terms
        # (biological_process, cellular_component, molecular_function)
        go_net.add_edges_from(
            [(top_go, 'GO:root')
             for top_go in ['GO:0003674', 'GO:0005575', 'GO:0008150']])

        # prune tree for computationl feasibility
        for i in range(prune_steps):
            cur_leaves = [n for n in go_net.nodes()
                          if go_net.in_degree(n) == 0]
            go_net.remove_nodes_from(cur_leaves)
            print(f'#{i} pruning step: removed {len(cur_leaves)} nodes')

        # fill GO-terms inclusively
        # (upstream terms contain all downstream genes)
        result: Dict[str, Set[str]] = {}

        def assign_upstream_terms(current_term: str) -> None:
            assert current_term in result, current_term

            neighs = go_net.neighbors(current_term)
            for n in neighs:
                # include the following new terms:
                #  * previously assigned terms (if any)
                #  * all downstream terms
                #  * own terms (if any)
                result[n] = \
                    result.get(n, set()) | \
                    result[current_term] | \
                    raw_associations.get(n, set())

                assign_upstream_terms(n)

        # set generous upper-bound for recursion limit
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(len(go_net))

        leaves = [n for n in go_net.nodes() if go_net.in_degree(n) == 0]
        for l in tqdm(leaves, desc='Traversing GO-Network'):
            # term might be in GO-network, but not in GO-associations
            # => term has no associated genes
            result[l] = raw_associations.get(l, set())

            assign_upstream_terms(l)

        sys.setrecursionlimit(old_limit)
    else:
        result = raw_associations

    # make sure gene-ids are strings
    result = {term: set(map(str, genes)) for term, genes in result.items()}

    return result
