#!/usr/bin/env python
# Copyright (C) 2019 Emanuel Goncalves

import numpy as np
import crispy as cy
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr


if __name__ == '__main__':
    dfiles = {
        'DOXY.Day30.Rep1': 'DOXY.Day30.Rep1.sgrna_summary.txt', 'DOXY.Day30.Rep2': 'DOXY.Day30.Rep2.sgrna_summary.txt',
        'DOXY.Day35.Rep1': 'DOXY.Day35.Rep1.sgrna_summary.txt', 'DOXY.Day35.Rep2': 'DOXY.Day35.Rep2.sgrna_summary.txt'
    }

    ddfs = {
        k: pd.read_csv(f'data/rescue/mageck/{dfiles[k]}', sep='\t', index_col=0) for k in dfiles
    }

    comparison = 'DOXY.Day30.Rep1'

    # Replicates correlation
    for day in [30, 35]:
        x, y = f'DOXY.Day{day}.Rep1', f'DOXY.Day{day}.Rep2'

        plot_df = pd.concat([
            ddfs[x]['LFC'].rename(x), ddfs[y]['LFC'].rename(y)
        ], axis=1, sort=False).dropna()

        g = sns.JointGrid(data=plot_df, x=x, y=y)

        g.plot_joint(plt.scatter, color=cy.QCplot.PAL_DBGD[0], s=40, edgecolor='white', alpha=.5)

        g.annotate(pearsonr)

        plt.gcf().set_size_inches(3, 3)
        plt.savefig(f'reports/rescue/mageck_DOXY_Day{day}_sgrna_corrplot.png', bbox_inches='tight', dpi=300)
        plt.close('all')

    # Timepoint correlation
    for rep in [1, 2]:
        x, y = f'DOXY.Day30.Rep{rep}', f'DOXY.Day35.Rep{rep}'

        plot_df = pd.concat([
            ddfs[x]['LFC'].rename(x), ddfs[y]['LFC'].rename(y)
        ], axis=1, sort=False).dropna()

        g = sns.JointGrid(data=plot_df, x=x, y=y)

        g.plot_joint(plt.scatter, color=cy.QCplot.PAL_DBGD[0], s=40, edgecolor='white', alpha=.5)

        g.annotate(pearsonr)

        plt.gcf().set_size_inches(3, 3)
        plt.savefig(f'reports/rescue/mageck_DOXY_Replicate{rep}_sgrna_corrplot.png', bbox_inches='tight', dpi=300)
        plt.close('all')

    #
    pos_sgrnas = pd.concat([ddfs[k].query('LFC > 5').add_prefix(f'{k}.') for k in ddfs], axis=1, sort=False).dropna()
    pos_sgrnas.to_csv('data/rescue/mageck/positive_lfc_sgrnas_all.csv')
    print(pos_sgrnas['DOXY.Day30.Rep1.Gene'].value_counts())


    #
    sgrnas = pd.read_csv('/Users/eg14/Data/gdsc/crispr/KY_Library_v1.1.csv', sep='\t', index_col=0)

    efiles = [f'DOXY.Day{day}.Rep{rep}' for day in [30, 35] for rep in [1, 2]]
    plot_df = pd.concat([ddfs[f]['LFC'].rename(f) for f in efiles], axis=1, sort=False).dropna()
    plot_df = plot_df[(plot_df > 5).sum(1) == 4]

    plot_df.to_csv('/Users/eg14/Downloads/DOXY.WRN.top_hits.csv')

    jscores = pd.read_csv('/Users/eg14/Data/gdsc/crispr/grna_efficacy_v1.1.tab', sep='\t')
    jscores = jscores[jscores['Gene'].isin(['SUPT3H', 'SUPT7L', 'TADA1', 'TAF6L'])]
    jscores = jscores.sort_values('Efficacy', ascending=False)
    jscores['sequence'] = sgrnas.loc[jscores['#gRNA']]['gRNA sequence'].values

    jscores.to_clipboard()
