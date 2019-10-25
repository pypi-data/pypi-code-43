import pandas as pd

from gene_map import GeneMapper


def load_cosmic(fname: str = 'data/CosmicMutantExport.tsv.gz') -> pd.DataFrame:
    """ Load cancer mutation data from COSMIC
    """
    df_mut = pd.read_csv(fname, sep='\t')

    # convert Gene_Name to GeneID (ENTREZ)
    gm = GeneMapper()
    gm_map = gm.query(
        df_mut['Gene name'].tolist(),
        source_id_type='Gene_Name', target_id_type='GeneID')

    gm_map.rename(
        columns={'ID_from': 'Gene name', 'ID_to': 'ENTREZ ID'}, inplace=True)
    df_mut = df_mut.merge(gm_map, on='Gene name')

    # extract somatic driver mutations
    df_mut_sig = df_mut[
        (df_mut['FATHMM score'] > .95) &
        (df_mut['Mutation somatic status'] == 'Confirmed somatic variant')]
    return df_mut_sig
