from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot
import numpy as np
import pandas as pd
import pybedtools as pbt

import matplotlib
# handle matplot lib backend nonsense
matplotlib.use('agg')


def multijaccard(beds, names=None, prefix='jaccard'):
    """
    Run bedtools jaccard for pairs of samples and plot as heatmap

    Parameters
    ==========
    beds : list<str>
        BED file paths
    names : list<str>
        Labels for BED files instead of generic 1:N. Assumed to be same length
        as `beds`.
    prefix : str
        Prefix for output files
    """
    # placeholder for resultant data
    results = pd.DataFrame(columns=[
        'Label 1', 'Label 2', 'Sample 1', 'Sample 2', 'intersection',
        'union-intersection', 'jaccard', 'n_intersections'])
    for i, a in enumerate(tqdm(beds)):
        # initialize res dictionary
        if names is not None:
            res = {'Sample 1': a, 'Label 1': names[i]}
        else:
            res = {'Sample 1': a, 'Label 1': int(i)}
        bedA = pbt.BedTool(a)
        for j, b in enumerate(beds[i:]):
            bedB = pbt.BedTool(b)
            # add second sample file
            res['Sample 2'] = b
            if names is not None:
                res['Label 2'] = names[i + j]
            else:
                res['Label 2'] = int(i + j)
            # add dictionary result from bedtools jaccard to res
            res.update(bedA.jaccard(bedB))
            # append this as a new record in the DataFrame
            results.loc[len(results)] = res
    # save output table
    results.to_csv(prefix + '.tsv', sep='\t', index=False)
    # pivot for heatmap
    jaccard = results.pivot('Label 2', 'Label 1', 'jaccard')
    # mask for clean plotting
    mask = np.zeros_like(jaccard)
    mask[np.triu_indices_from(mask, 1)] = True
    g = sns.heatmap(jaccard, annot=True, fmt='.2f', mask=mask,
                    square=True, annot_kws={"size": 8})
    g.get_figure().savefig(prefix + '.pdf', figsize=(2 * len(beds)))
