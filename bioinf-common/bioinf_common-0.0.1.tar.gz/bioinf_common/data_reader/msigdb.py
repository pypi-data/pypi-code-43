from tqdm import tqdm as tqdm


def load_msigdb(data_dir='./data/MSigDB', min_size=0, max_size=None):
    """ Load all pathways from MSigDB:
         * c2: curated gene sets (KEGG, Reactome, BioCarta, ...)
         * c5: GO terms
    """
    result = {}
    fname = f'{data_dir}/c2.all.v6.1.entrez.gmt'
    with open(fname) as fd:
        for line in tqdm(fd.readlines()):
            name, url, *genes = line.split()

            if len(set(genes)) < min_size:
                continue

            if max_size is not None and len(set(genes)) > max_size:
                continue

            assert name not in result
            result[name] = set(map(str, genes))
    return result
