#!/usr/bin/env python
# Copyright (C) 2018 Emanuel Goncalves

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.stats.weightstats import ztest
from CrispyPlot import MidpointNormalize
from crispy.Bedit import BeditPlot, Modifications, CrispyPlot
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import WhiteKernel, ConstantKernel, RBF

PPDIR = '/Users/eg14/Data/resources/phosphositeplus/'

CONDITIONS = ['A549_p53WT_Nutlin-3_Z-score', 'A549_p53NULL_Nutlin-3_Z-score', 'A549_p53NULL_Etoposide_Z-score']

KSNET = pd.read_csv(f'{PPDIR}/Kinase_Substrate_Dataset.txt', sep='\t', skiprows=3)\
    .query("KIN_ORGANISM == 'human'").query("SUB_ORGANISM == 'human'").query("SUB_GENE == 'TP53'")

KSNET_DICT = KSNET.groupby('GENE')['SUB_MOD_RSD'].agg(set).to_dict()


def calculate_kinase_activity(dataset, ksnet=None, conditions=None):
    if ksnet is None:
        ksnet = KSNET

    if conditions is None:
        conditions = CONDITIONS

    ksnet = ksnet.groupby('GENE')['SUB_MOD_RSD'].agg(set).to_dict()

    # Activities
    kact = []
    for c in conditions:
        fcs = dataset[[c, 'residue']].dropna()

        ksnet = {k: ksnet[k].intersection(fcs['residue']) for k in ksnet}
        ksnet = {k: ksnet[k] for k in ksnet if len(ksnet[k]) > 1}

        for k in ksnet:
            zscore, pvalue = ztest(
                fcs[fcs['residue'].isin(ksnet[k])][c], fcs[~fcs['residue'].isin(ksnet[k])][c]
            )

            kact.append(dict(condition=c, kinase=k, zscore=zscore, pvalue=pvalue, res=';'.join(ksnet[k])))

    kact = pd.DataFrame(kact).sort_values('pvalue')

    return kact


def scatter_matrix(dataframe):
    for condition in CONDITIONS:
        f, axs = plt.subplots(len(set(dataframe['AA_variant'])), 1, sharex='all', sharey='all')

        axs[0].set_title(condition)

        for i, (variant, df) in enumerate(dataframe.groupby('AA_variant')):
            axs[i].scatter(
                df['Position'], df[condition], s=1, c=df[condition], cmap='RdYlBu', norm=MidpointNormalize(midpoint=0.), alpha=.7
            )

            axs[i].axhline(0, ls='--', lw=.3, c=CrispyPlot.PAL_DBGD[2], zorder=0)

            axs[i].set_ylabel(variant)

        plt.gcf().set_size_inches(8, 8)
        plt.savefig(f'reports/bedit/TP53_scatter_grid_{condition}.pdf', bbox_inches='tight', transparent=True)
        plt.close('all')


def gpr_calculations():
    gprs_df = []
    for aa, df in screen.groupby('AA_variant'):
        for condition in CONDITIONS:
            aa_label = condition.replace('_Z-score', '')

            #
            kernel = ConstantKernel() * RBF() + WhiteKernel()

            gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=3)
            gpr = gpr.fit(df[['Position']], df[condition])
            print(aa, gpr)

            y_pred, y_std = gpr.predict(df[['Position']], return_std=True)

            df[f'{aa_label}_gprmean'] = y_pred
            df[f'{aa_label}_gprstd'] = y_std
            df[f'{aa_label}_delta'] = df[condition] - df[f'{aa_label}_gprmean']

        gprs_df.append(df)

    gprs_df = pd.concat(gprs_df)

    k_activity = calculate_kinase_activity(gprs_df, conditions=[c for c in gprs_df if c.endswith('_delta')])

    return gprs_df, k_activity


# condition = 'A549_p53NULL_Etoposide_Z-score'
def scatter_aa(condition):
    plot_df, k_activity = gpr_calculations()

    label = condition.replace('_Z-score', '')

    #
    df = plot_df[~plot_df['AA_variant'].isin(['Z', 'B'])]
    plt.scatter(
        df['Position'], df[condition], s=1, c=df[condition], cmap='RdYlBu', norm=MidpointNormalize(midpoint=0.), alpha=.7
    )

    #
    for aa, df in plot_df.groupby('AA_variant'):
        if aa == 'B':
            plt.plot(df['Position'], df[f'{label}_gprmean'], ls='-', lw=1., c='#31a354', label='Synonymous')

        elif aa == 'Z':
            plt.plot(df['Position'], df[f'{label}_gprmean'], ls='-', lw=1., c='#e34a33', label='STOP')

        else:
            plt.plot(df['Position'], df[f'{label}_gprmean'], ls='-', lw=1., c=CrispyPlot.PAL_DBGD[0], label=None, alpha=0)

    #
    for k in ['DAPK1']:
        for sub in KSNET_DICT[k]:
            plt.axvline(int(sub[1:]), ls='-', lw=.3, c=CrispyPlot.PAL_DBGD[1], label=sub)

    #
    plt.axhline(0, ls='-', lw=.3, c=CrispyPlot.PAL_DBGD[2], zorder=0, alpha=.8)
    plt.grid(ls='--', lw=.5, color=CrispyPlot.PAL_DBGD[2], zorder=0, axis='x', alpha=.8)

    #
    plt.title(condition)
    plt.xlabel('AA position')
    plt.ylabel('Fitness score')

    #
    plt.gcf().set_size_inches(5, 3)
    plt.savefig(f'reports/bedit/TP53_scatter_{condition}.pdf', bbox_inches='tight', transparent=True)
    plt.close('all')


if __name__ == '__main__':
    # -
    """
        Variant resolution data/information
            - Mutation calls (Cell lines + Tumours)
            - Kinase/subtrate residues
            - Regulatory residues
            - Proteomics coverage      
    """

    # -
    # screen = pd.read_excel('data/bedit/giacomelli_2018/41588_2018_204_MOESM5_ESM.xlsx', skiprows=1)
    screen = pd.read_excel('data/bedit/giacomelli_2018/41588_2018_204_MOESM6_ESM.xlsx', skiprows=1).iloc[:, :7]

    #
    screen['residue'] = screen['AA_wt'] + screen['Position'].astype(str)

    screen['wildtype'] = screen['AA_wt'].replace({'Z': '*'}).replace(Modifications.get_names())
    screen['mutant'] = screen['AA_variant'].replace({'Z': '*'}).replace(Modifications.get_names())

    screen['phosphomimetic'] = (screen['AA_wt'].isin(['S', 'T', 'Y']) & screen['AA_variant'].isin(['D', 'E'])).replace({True: 'Yes', False: 'No'})

    #
    plot_df, k_activity = gpr_calculations()

    #
    tcga_mut = pd.read_csv('/Users/eg14/Data/tcga/TCGA.6col', sep='\t')
    tcga_mut_all = pd.read_csv('/Users/eg14/Data/tcga/mc3.v0.2.8.PUBLIC.maf.gz', sep='\t')

    #
    reg_phospho = pd.read_csv(f'{PPDIR}/Phosphorylation_site_dataset.txt', sep='\t', skiprows=3)\
        .query("ORGANISM == 'human'").query("GENE == 'TP53'")
    reg_phospho = reg_phospho[reg_phospho['MOD_RSD'].apply(lambda v: v[0] in ['S', 'T', 'Y'])]
    reg_phospho['MOD_RSD'] = reg_phospho['MOD_RSD'].apply(lambda v: v.split('-')[0])
    screen['phosphorylation'] = screen['residue'].isin(reg_phospho['MOD_RSD']).replace({True: 'Yes', False: 'No'})

    reg_acetyl = pd.read_csv(f'{PPDIR}/Acetylation_site_dataset.txt', sep='\t', skiprows=3) \
        .query("ORGANISM == 'human'").query("GENE == 'TP53'")
    reg_acetyl['MOD_RSD'] = reg_acetyl['MOD_RSD'].apply(lambda v: v.split('-')[0])
    screen['acetylation'] = screen['residue'].isin(reg_acetyl['MOD_RSD']).replace({True: 'Yes', False: 'No'})

    reg_ubi = pd.read_csv(f'{PPDIR}/Ubiquitination_site_dataset.txt', sep='\t', skiprows=3) \
        .query("ORGANISM == 'human'").query("GENE == 'TP53'")
    reg_ubi['MOD_RSD'] = reg_ubi['MOD_RSD'].apply(lambda v: v.split('-')[0])
    screen['ubiquitination'] = screen['residue'].isin(reg_ubi['MOD_RSD']).replace({True: 'Yes', False: 'No'})

    #
    regsites = pd.read_csv(f'{PPDIR}/Regulatory_sites.txt', sep='\t', skiprows=3)\
        .query("ORGANISM == 'human'").query("GENE == 'TP53'")

    # - Matrix
    for condition in CONDITIONS:
        smatrix = pd.pivot_table(screen, index=['Position', 'AA_wt'], columns='AA_variant', values=condition)

        #
        sns.clustermap(
            smatrix.corr(method='spearman'), annot=True, fmt='.1f', cmap='RdYlBu', center=0, annot_kws=dict(size=4)
        )

        plt.gcf().set_size_inches(6, 6)
        plt.savefig(f'reports/bedit/TP53_variant_clustermap_{condition}.pdf', bbox_inches='tight', transparent=True)
        plt.close('all')

        #
        sns.clustermap(
            smatrix.T.corr(method='spearman'), cmap='RdYlBu', center=0
        )

        plt.gcf().set_size_inches(6, 6)
        plt.savefig(f'reports/bedit/TP53_wt_clustermap_{condition}.pdf', bbox_inches='tight', transparent=True)
        plt.close('all')

    # - Kinase activity
    # Kinase-substrate network
    ksnet = pd.read_csv(f'{PPDIR}/Kinase_Substrate_Dataset.txt', sep='\t', skiprows=3)\
        .query("KIN_ORGANISM == 'human'").query("SUB_ORGANISM == 'human'").query("SUB_GENE == 'TP53'")

    screen[screen['residue'].isin(ksnet.query("GENE == 'CDK7'")['SUB_MOD_RSD'])]

    # -
    BeditPlot.aa_grid(screen)
    plt.gcf().set_size_inches(9, 9)
    plt.savefig(f'reports/bedit/TP53_aa_grid.pdf', bbox_inches='tight', transparent=True)
    plt.close('all')

    BeditPlot.aa_countplot(screen)
    plt.gcf().set_size_inches(2, 4)
    plt.savefig(f'reports/bedit/TP53_aa_countplot.pdf', bbox_inches='tight', transparent=True)
    plt.close('all')

    # -
    for mtype in ['phosphomimetic', 'acetylation', 'ubiquitination', 'phosphorylation']:
        plot_df = pd.melt(screen, id_vars=mtype, value_vars=CONDITIONS)

        pal = {'Yes': BeditPlot.PAL_DBGD[1], 'No': BeditPlot.PAL_DBGD[2]}

        sns.boxplot(
            'value', 'variable', hue=mtype, data=plot_df, orient='h', palette=pal, saturation=1., showcaps=False,
            notch=True, medianprops=BeditPlot.MEDIANPROPS, flierprops=BeditPlot.FLIERPROPS, boxprops=BeditPlot.BOXPROPS,
            whiskerprops=BeditPlot.WHISKERPROPS
        )

        lgd = plt.legend(frameon=False, loc=2, prop={'size': 4}, title=mtype.capitalize())
        lgd._legend_box.align = 'left'
        lgd.get_title().set_fontsize(4)

        plt.gcf().set_size_inches(3, 1)
        plt.savefig(f'reports/bedit/TP53_aa_{mtype}_boxplot.pdf', bbox_inches='tight', transparent=True)
        plt.close('all')
