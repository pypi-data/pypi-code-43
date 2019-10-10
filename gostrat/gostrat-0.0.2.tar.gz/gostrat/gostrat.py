#!/usr/bin/env python3
'''
Usage:
    gostrat generate_gmt [options]
    gostrat (strat|stratify) [options] [-p CUTOFF ] <gsea_fn>...
    
Options:
    -h --help               helpful help
    -o FN --output=FN       output filename [default: stdout]
    -g FN --gmt=FN          output filename for gmt file [default: go_<timestamp>.gmt]
    -t TID --taxon=TID      taxon of organism to download gene2go annotations,
                            default is human [default: 9606]
    -i TYPE --id-type=TYPE  gene identifier type, one of symbol, entrez, or
                            ensembl.gene [default: symbol]
    -p CUTOFF               cutoff to use to identify significant genesets [default: 0.05]
    -q --quiet              shut up output
'''

from collections import defaultdict
import csv
import datetime
from docopt import docopt
from de_toolkit.enrich import GMT
import goatools
from goatools.anno.genetogo_reader import Gene2GoReader
from goatools.base import download_go_basic_obo
from goatools.base import download_ncbi_associations
from goatools.obo_parser import GODag
import io
import logging
import mygene
import pandas

import os
import sys

logging.basicConfig(level=logging.INFO)

class LogWriter(object):
    def __init__(self) :
        pass
    def write(self,*msg) :
        logging.info(' '.join(msg).strip())

def main(args=sys.argv[1:]) :

    args = docopt(__doc__,argv=args)

    if args['--quiet'] :
        logging.basicConfig(level=logging.WARN)

    log_writer = LogWriter()

    obo_fname = download_go_basic_obo(prt=log_writer, loading_bar=False)

    obodag = GODag("go-basic.obo",prt=log_writer)

    fin_gene2go = download_ncbi_associations(prt=log_writer)

    # Read NCBI's gene2go. Store annotations in a list of namedtuples
    logging.info('Gene2GoReader')
    objanno = Gene2GoReader(fin_gene2go,
            taxids=[int(args['--taxon'])],
            prt=log_writer
    )
    logging.info('Gene2GoReader done')

    if args['generate_gmt'] :

        logging.info('MyGene entrez to symbol mapping')
        mg = mygene.MyGeneInfo()
        gene_map = mg.getgenes(
            objanno.get_id2gos_nss().keys(),
            'entrez,{}'.format(args['--id-type']),
            as_dataframe=True
        )
        gene_map = gene_map.loc[~gene_map.index.duplicated()]
        gene_map.rename(columns={'_id':'entrez'},inplace=True)
        
        # create a GMT file for use later in fgsea from these annotations
        gmt = {}

        entrez_id_map = dict(_ for _ in gene_map[['entrez',args['--id-type']]].itertuples(index=False))

        for go, ids in objanno.get_goid2dbids(objanno.associations).items() :
            gmt[go] = [entrez_id_map.get(str(_)) for _ in ids]
            gmt[go] = [_ for _ in gmt[go] if _ is not None]
        gmt = GMT(gmt)
        
        out_fn = args['--gmt']
        if out_fn == 'go_<timestamp>.gmt' :
            out_fn = 'go_{}.gmt'.format(datetime.datetime.now().isoformat())
        
        with open(out_fn,'w') as f :
            out_f = csv.writer(f,delimiter='\t')
            for gs, genes in gmt.items() :
                term = obodag.get(gs)
                if term is None :
                    logging.warn('GO term {} with genes {} was not identified in the goatools.obodag, skipping'.format(gs,genes))
                    continue
                out_f.writerow(
                        [gs,'{}, NS={}'.format(term.name,term.namespace)]+list(genes)
                )

    elif args['strat'] or args['stratify'] :

        import networkx as nx

        # each FN should have a first column as a GO term and
        # a column named 'padj'
        fns = args['<gsea_fn>']

        goea_results = {}
        go_superset = set()
        goea_dfs = []

        cutoff = float(args['-p'])

        for fn in fns :

            df = pandas.read_csv(fn,index_col=0,sep=None,engine='python')

            # column named padj required
            assert 'padj' in df.columns

            sig_df = df.loc[df['padj']<cutoff]
            goea_results[fn] = sig_df.index.tolist()

            # keep track of gene sets that are significant in any analysis
            go_superset = go_superset.union(set(goea_results[fn]))

            basename = os.path.splitext(os.path.basename(fn))[0]
            df.rename(columns={_:'{}__{}'.format(basename,_) for _ in df.columns},inplace=True)
            goea_dfs.append(df)

        goea_df = goea_dfs[0]
        for df in goea_dfs[1:] :
            goea_df = goea_df.merge(df,left_index=True,right_index=True,how='outer')

        orig_cols = goea_df.columns.tolist()
        goea_df['ns'] = ''
        goea_df['parent_id'] = ''
        goea_df['parent_name'] = ''
        goea_df['term_name'] = ''
        goea_df = goea_df[['ns','parent_id','parent_name','term_name']+orig_cols]

        ns_g = defaultdict(nx.DiGraph)
        for k,terms in goea_results.items():
            for term in terms :

                term = obodag.get(term)

                # filter nodes from paths that aren't enriched
                paths = []
                for path in obodag.paths_to_top(term.id) :
                    paths.append([_.id for _ in path if _.id in go_superset or len(_.parents) == 0 ])

                # pick only the longest path to add to the graph
                longest_subpath = sorted(paths,key=lambda _: -len(_))[0]

                # reverse the path so it goes from root to leaf
                longest_subpath = longest_subpath#[::-1]
                for t1, t2 in zip(longest_subpath[:-1],longest_subpath[1:]) :
                    ns_g[term.namespace].add_edge(t1,t2)

        # iterate through each namespace
        for ns, g in ns_g.items() :
            root_path = obodag.paths_to_top(list(g.nodes)[0])[0]
            root = root_path[0]

            # take first children
            for node in list(g.successors(root.id)) :

                descendants = nx.algorithms.dag.descendants(g,node)
                descendants = list(descendants)+[node]

                for desc in descendants :
                    goea_df.loc[desc,['ns','parent_id','parent_name','term_name']] = [
                            ns,
                            node,
                            obodag.get(node).name,
                            obodag.get(desc).name
                        ]

        out_f = sys.stdout if args['--output'] == 'stdout' else open(args['--output'],'w')
 
        goea_df.sort_values(['ns','parent_id']).to_csv(out_f)

if __name__ == '__main__' :

    
    main()
