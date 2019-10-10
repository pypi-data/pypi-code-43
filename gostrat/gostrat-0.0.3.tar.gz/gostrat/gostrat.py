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
    -v --verbose            loud output
    -q --quiet              shut up output
'''

from collections import defaultdict
import csv
import datetime
from docopt import docopt
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


class LogWriter(object):
    def __init__(self,name) :
        self.log = logging.getLogger(name)
    def write(self,*msg) :
        msg = [_.strip() for _ in msg if _.strip() != '']
        if len(msg) > 0 :
            self.log.info(' '.join(msg).strip())
    def flush(self) :
        pass

def get_genemap(objanno) :
    mg = mygene.MyGeneInfo()
    gene_map = mg.getgenes(
        objanno.get_id2gos_nss().keys(),
        'entrez,name,symbol,ensembl.gene',
        as_dataframe=True
    )
    gene_map = gene_map.loc[~gene_map.index.duplicated()]
    gene_map.rename(columns={'_id':'entrez'},inplace=True)
    gene_map.index = gene_map['entrez']
    gene_map.fillna('noidmap',inplace=True)
    return gene_map

def main(args=sys.argv[1:]) :

    args = docopt(__doc__,argv=args)

    id_types = ('symbol','entrez','ensembl.gene')
    if args['--id-type'] not in id_types :
        logging.error('invalid --id-type specified {}, must be one of {}'.format(args['--id-type'],id_types))
        sys.exit(1)

    level = logging.INFO
    if args['--verbose'] :
        level = logging.DEBUG
    elif args['--quiet'] :
        level = logging.WARN

    logging.basicConfig(level=level)

    goa_log = LogWriter('goatools')

    obo_fname = download_go_basic_obo(prt=goa_log, loading_bar=False)

    obodag = GODag("go-basic.obo",prt=goa_log)

    fin_gene2go = download_ncbi_associations(prt=goa_log)

    # Read NCBI's gene2go. Store annotations in a list of namedtuples
    logging.debug('Gene2GoReader')

    # goatools Gene2GoReader hardcodes its print output to sys.stdout
    # monkeypatch it
    old_stdout = sys.stdout
    sys.stdout = goa_log
    objanno = Gene2GoReader(fin_gene2go,
            taxids=[int(args['--taxon'])],
            prt=goa_log
    )
    sys.stdout = old_stdout
    logging.debug('Gene2GoReader done')

    if args['generate_gmt'] :

        logging.info('mapping entrez to symbol')
        genemap_fn = 'gene2go_genemap.csv'
        if os.path.exists(genemap_fn) :
            logging.info('found existing genemap file {}, loading'.format(genemap_fn))
            gene_map = pandas.read_csv(genemap_fn)

            if args['--id-type'] not in gene_map.columns :
                # someone messed with the gene map file
                logging.info('{} not found in gene map, updating gene map'.format(args['--id-type'],genemap_fn))
                gene_map = get_genemap(objanno)

                gene_map.to_csv(genemap_fn)
        else :
            logging.info('no existing genemap file found, generating'.format(genemap_fn))
            gene_map = get_genemap(objanno)
            gene_map.to_csv(genemap_fn)

       
        # create a GMT file for use later in fgsea from these annotations
        gmt = {}

        entrez_id_map = dict(_ for _ in gene_map[['entrez',args['--id-type']]].itertuples(index=False))

        # remove nan identifiers, sometimes they exist
        entrez_id_map = {k:v for k,v in entrez_id_map.items() if not pandas.isnull(v)}

        logging.debug('first 10 entrez_id_map')
        logging.debug({k:entrez_id_map[k] for k in list(entrez_id_map.keys())[:10]})

        for go, ids in objanno.get_goid2dbids(objanno.associations).items() :
            gmt[go] = [entrez_id_map.get(_) for _ in ids]
            gmt[go] = [_ for _ in gmt[go] if _ is not None]
        logging.debug('last GO gmt record: {}'.format(gmt[go]))

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
