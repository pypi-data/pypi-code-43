#!/usr/bin/env python
# Copyright (C) 2019 Emanuel Goncalves

import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from crispy import CrispyPlot, QCplot, Utils


class OrganoidsBME:
    def __init__(self, ddir='data/organoids/bme/', plasmid='Plasmid_v1.1', pseudocount=1):
        self.pseudocount = pseudocount

        self.dir = ddir

        self.plasmid = plasmid

        self.samplesheet = self.import_samplesheet()

        self.library = self.import_library()

        self.rawcounts = self.import_rawcounts()
        self.rawcounts = self.rawcounts.rename(columns=self.samplesheet['name'])

        self.fc_sgrna = self.foldchanges_sgrna()
        self.fc_gene = self.fc_sgrna.groupby(self.library.loc[self.fc_sgrna.index, 'GENES']).mean()

    def import_rawcounts(self):
        dfiles = [f for f in os.listdir(self.dir) if f.endswith('.read_count.tsv')]

        rawcounts = pd.concat([
            pd.read_csv(f'{self.dir}/{f}', sep='\t', index_col=0).drop(['gene'], axis=1) for f in dfiles
        ], axis=1, sort=False)

        rawcounts = rawcounts.groupby(rawcounts.columns, axis=1).mean()

        return rawcounts

    def import_samplesheet(self):
        return pd.read_csv(f'{self.dir}/samplesheet.csv', index_col=0)

    def import_library(self, dfile='KY_Library_v1.1_annotated.csv'):
        return pd.read_csv(f'{self.dir}/{dfile}', index_col=0)

    def foldchanges_sgrna(self):
        foldchanges = self.rawcounts\
            .add(self.pseudocount)\
            .divide(self.rawcounts[self.plasmid], axis=0)\
            .drop(self.plasmid, axis=1)\
            .apply(np.log2)

        return foldchanges


if __name__ == '__main__':
    data = OrganoidsBME()

    # -
    QCplot.plot_cumsum_auc(data.fc_gene, Utils.get_non_essential_genes())

    # - Clustermap raw counts
    sns.clustermap(data.rawcounts.corr(), cmap='RdYlBu', center=0, annot=True, fmt='.1f', annot_kws=dict(size=4))
    plt.gcf().set_size_inches(3, 3)
    plt.savefig(f'reports/bme/clustermap_rawcounts.pdf', bbox_inches='tight', dpi=600)
    plt.close('all')

    # - Clustermap sgrna fold-changes
    sns.clustermap(data.fc_sgrna.corr(), cmap='RdYlBu', center=0, annot=True, fmt='.1f', annot_kws=dict(size=4))
    plt.gcf().set_size_inches(3, 3)
    plt.savefig(f'reports/bme/clustermap_foldchange_sgrna.pdf', bbox_inches='tight', dpi=600)
    plt.close('all')

    # - Clustermap gene fold-changes
    sns.clustermap(data.fc_gene.corr(), cmap='RdYlBu', center=0, annot=True, fmt='.1f', annot_kws=dict(size=4))
    plt.gcf().set_size_inches(3, 3)
    plt.savefig(f'reports/bme/clustermap_foldchange_gene.pdf', bbox_inches='tight', dpi=600)
    plt.close('all')

    # -
    plot_df = data.fc_gene.unstack().rename('fc').reset_index()
    sns.boxplot('fc', 'level_0', orient='h', data=plot_df, color=CrispyPlot.PAL_DBGD[0], saturation=1, flierprops=CrispyPlot.FLIERPROPS)
    plt.title('Gene fold-changes')
    plt.gcf().set_size_inches(3, 2)
    plt.savefig(f'reports/bme/boxplots_foldchange_gene.pdf', bbox_inches='tight', dpi=600)
    plt.close('all')

    # -
    plot_df = data.fc_sgrna.unstack().rename('fc').reset_index()
    sns.boxplot('fc', 'level_0', orient='h', data=plot_df, color=CrispyPlot.PAL_DBGD[0], saturation=1, flierprops=CrispyPlot.FLIERPROPS)
    plt.title('sgRNA fold-changes')
    plt.gcf().set_size_inches(3, 2)
    plt.savefig(f'reports/bme/boxplots_foldchange_sgrna.pdf', bbox_inches='tight', dpi=600)
    plt.close('all')

    # - Total counts barplot
    plot_df = pd.concat([
        data.rawcounts.sum().rename('Total reads'), data.samplesheet.set_index('name')
    ], axis=1, sort=False).reset_index()

    sns.barplot(x='Total reads', y='index', data=plot_df, color=CrispyPlot.PAL_DBGD[0])

    plt.title('Total raw counts')
    plt.ylabel('')

    plt.gcf().set_size_inches(2, 2)
    plt.savefig(f'reports/bme/rawcounts_total_barplot.pdf', bbox_inches='tight', transparent=True)
    plt.close('all')

    # - Guides above count threshold
    count_thres = 10

    plot_df = pd.concat([
        (data.rawcounts > count_thres).sum().rename('total'), data.samplesheet.set_index('name')
    ], axis=1, sort=False).reset_index()

    sns.barplot(x='total', y='index', data=plot_df, color=CrispyPlot.PAL_DBGD[0])

    plt.title(f'sgRNAs with counts > {count_thres}')
    plt.ylabel('Number of sgRNAs')

    plt.gcf().set_size_inches(2, 2)
    plt.savefig(f'reports/bme/rawcounts_threshold_barplot.pdf', bbox_inches='tight', transparent=True)
    plt.close('all')
