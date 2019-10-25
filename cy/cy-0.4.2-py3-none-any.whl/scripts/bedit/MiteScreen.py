#!/usr/bin/env python
# Copyright (C) 2019 Emanuel Goncalves

import os
import logging
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from crispy.Bedit import CrispyPlot
from statsmodels.stats.weightstats import ztest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import ShuffleSplit
from sklearn.ensemble import RandomForestRegressor
from crispy.CircularBinarySegmentation import CBS


class MutFunc:
    def __init__(self, ddir='data/bedit/mutfunc_tp53/'):
        self.ddir = ddir

        self.dfiles = [f for f in os.listdir(self.ddir) if f.endswith('.tab')]

        self.results = {
            f.split('.')[0]: self.read_file(f) for f in self.dfiles
        }

    @staticmethod
    def to_mutfunc(mitescreen, uniprot='P04637'):
        return pd.Series([f'{uniprot} {i}' for i in mitescreen.df.index])

    def read_file(self, dfile='conservation.tab'):
        df = pd.read_csv(f'{self.ddir}/{dfile}', comment='#', sep='\t')
        df['allele'] = df['refaa'] + df['posaa'].astype(str) + df['altaa']
        return df


class KinaseActivity:
    def __init__(self, ppdir='/Users/eg14/Data/resources/phosphositeplus/', filter_gene='TP53', organism='human'):
        self.ppdir = ppdir

        self.ksnet = pd.read_csv(f'{self.ppdir}/Kinase_Substrate_Dataset.txt', sep='\t', skiprows=3)

        if organism is not None:
            self.ksnet = self.ksnet.query(f"KIN_ORGANISM == '{organism}'").query(f"SUB_ORGANISM == '{organism}'")

        if filter_gene is not None:
            self.ksnet = self.ksnet.query(f"SUB_GENE == '{filter_gene}'")

    def calculate_kinase_activity(self, data, conditions):
        data = data.groupby('res').mean()[conditions]
        data = pd.DataFrame(StandardScaler().fit_transform(data), index=data.index, columns=data.columns)
        data = data.reset_index()

        kact = []

        for condition in conditions:
            ksnet = self.ksnet.groupby('GENE')['SUB_MOD_RSD'].agg(set).to_dict()

            ksnet = {k: ksnet[k].intersection(data['res']) for k in ksnet}
            ksnet = {k: ksnet[k] for k in ksnet if len(ksnet[k]) > 1}

            for k in ksnet:
                zscore, pvalue = ztest(
                    data[data['res'].isin(ksnet[k])][condition], data[~data['res'].isin(ksnet[k])][condition]
                )

                kact.append(dict(
                    kinase=k, zscore=zscore, pvalue=pvalue, res=';'.join(ksnet[k]), condition=condition,
                    mean=data[data['res'].isin(ksnet[k])][condition].mean()
                ))

        kact = pd.DataFrame(kact).sort_values('pvalue')

        return kact


class MiteScreen:
    CONDITIONS = ['p53WT_Nutlin-3', 'p53NULL_Nutlin-3', 'p53NULL_Etoposide']

    def __init__(self, dfile=f'data/bedit/giacomelli_2018/41588_2018_204_MOESM6_ESM.xlsx'):
        self.df = pd.read_excel(dfile, skiprows=1, index_col=0).iloc[:, :6]
        self.mutfunc = MutFunc('data/bedit/mutfunc_tp53/')

    def segments_mean(self, segments):
        conditions_norm = []

        for condition in self.CONDITIONS:
            condition_mean, condition_norm = [], []

            for i, end in enumerate(segments[condition]):
                if i != 0:
                    start = segments[condition][i - 1]

                    segment_aas = self.df.query(f'(posaa >= {start}) & (posaa < {end})')

                    segment_mean = segment_aas[condition].mean()

                    condition_mean.append(pd.Series(segment_mean, index=segment_aas.index))
                    condition_norm.append(segment_aas[condition] - segment_mean)

            conditions_norm.append(pd.concat([
                pd.concat(condition_mean).rename(f'{condition}_mean'),
                pd.concat(condition_norm).rename(f'{condition}')
            ], axis=1))

        conditions_norm = pd.concat(conditions_norm, axis=1)
        conditions_norm = pd.concat([conditions_norm, self.df[['refaa', 'altaa', 'posaa']]], axis=1, sort=False)
        conditions_norm['res'] = conditions_norm['refaa'] + conditions_norm['posaa'].astype(str)
        return conditions_norm.dropna()


if __name__ == '__main__':
    # - Import screen
    screen = MiteScreen()

    # -
    f, axs = plt.subplots(3, 1, sharex='all')

    segments = {}
    for i, condition in enumerate(screen.CONDITIONS):
        condition_matrix = pd.pivot_table(screen.df, index=['posaa', 'refaa'], columns='altaa', values=condition)

        aa_scores = condition_matrix.drop(columns=['B', 'Z']).mean(1)

        segments[condition] = CBS.run(aa_scores, shuffles=int(1e4), p=0.01)

        CBS.draw_segmented_data(aa_scores, segments[condition], ax=axs[i])
        axs[i].set_ylabel(condition)

    plt.gcf().set_size_inches(8, 4.5)
    plt.savefig(f'reports/bedit/TP53_CBS.pdf', bbox_inches='tight', transparent=True)
    plt.close('all')

    # -
    conditions_norm = screen.segments_mean(segments)

    kact = KinaseActivity()
    kact.calculate_kinase_activity(conditions_norm, screen.CONDITIONS)

    # -
    alleles = set.intersection(
        set(screen.df.index),
        set(screen.mutfunc.results['conservation']['allele']),
        set(screen.mutfunc.results['stability']['allele']),
    )
    print(f'#(Alleles)={len(alleles)}')

    df = pd.concat([
        screen.df.loc[alleles, screen.CONDITIONS],
        screen.df.loc[alleles, 'posaa'],
        screen.mutfunc.results['conservation'].set_index('allele').loc[alleles]['ic'],
        screen.mutfunc.results['conservation'].set_index('allele').loc[alleles]['score'],
        screen.mutfunc.results['stability'].set_index('allele').loc[alleles]['ddg'],
    ], axis=1)

    g = sns.PairGrid(df)

    g = g.map(plt.scatter, c=z, s=100, edgecolor='')

    plt.gcf().set_size_inches(6, 6)
    plt.savefig(f'reports/bedit/TP53_mutfunc_pairplot.pdf', bbox_inches='tight', transparent=True)
    plt.close('all')

    sns.pairplot(
        df, height=3, diag_kws=dict(shade=True),
        plot_kws=dict(s=10, edgecolor=CrispyPlot.PAL_DBGD[0], linewidth=.3, alpha=.5),
        diag_kind='kde'
    )
    plt.gcf().set_size_inches(6, 6)
    plt.savefig(f'reports/bedit/TP53_mutfunc_pairplot.pdf', bbox_inches='tight', transparent=True)
    plt.close('all')

    y = df[screen.CONDITIONS[0]]

    x = df.drop(columns=screen.CONDITIONS)
    x = pd.DataFrame(StandardScaler().fit_transform(x), index=x.index, columns=x.columns)

    lmres = []
    for train, test in ShuffleSplit(n_splits=100, test_size=.3).split(x, y):
        # lm = Ridge().fit(x.iloc[train], y.iloc[train])
        lm = RandomForestRegressor(n_estimators=100).fit(x.iloc[train], y.iloc[train])

        r2 = lm.score(x.iloc[test], y.iloc[test])

        lmres.append([r2])

    lmres = pd.DataFrame(lmres, columns=['r2'])
    print(f"R-squared: {lmres['r2'].median():.2f}")

    # -
    df_conservation = pd.concat([
        screen.df,
        screen.mutfunc.results['conservation'].set_index('allele')
    ], axis=1, sort=False).dropna()

    df_conservation.corr()['score'].sort_values()

    sns.regplot('p53WT_Nutlin-3', 'score', data=df_conservation)
    plt.show()

    # -
    df_interfaces = pd.concat([
        screen.mutfunc.results['interfaces'],
        screen.df.loc[screen.mutfunc.results['interfaces']['allele'], screen.CONDITIONS].reset_index()
    ], axis=1, sort=False).dropna()

    df_interfaces.corr()['p53WT_Nutlin-3'].sort_values()

    sns.boxplot(df_interfaces['impact'].astype(str), df_interfaces['p53WT_Nutlin-3'], notch=True)
    plt.show()

    # -
    df_linearmotifs = pd.concat([
        screen.mutfunc.results['linear_motifs'],
        screen.df.loc[screen.mutfunc.results['linear_motifs']['allele'], screen.CONDITIONS].reset_index()
    ], axis=1, sort=False).dropna()

    df_linearmotifs.corr()['p53WT_Nutlin-3'].sort_values()

    sns.boxplot(df_linearmotifs['impact'].astype(str), df_linearmotifs['p53WT_Nutlin-3'], notch=True)
    plt.show()

    sns.regplot('p53WT_Nutlin-3', 'pattern_probability', data=df_linearmotifs)
    plt.show()

    # -
    df_stability = pd.concat([
        screen.df,
        screen.mutfunc.results['stability'].set_index('allele')
    ], axis=1, sort=False).dropna()

    df_stability.corr()['p53WT_Nutlin-3'].sort_values()

    sns.regplot('p53WT_Nutlin-3', 'ddg', data=df_stability)
    plt.show()

