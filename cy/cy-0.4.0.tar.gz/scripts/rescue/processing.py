#!/usr/bin/env python
# Copyright (C) 2018 Emanuel Goncalves

import re
import os
import numpy as np
import crispy as cy
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from crispy import CrispyPlot
from scipy.stats import pearsonr


class DataImporter:
    def __init__(self, data_dir='data/rescue/', plasmid='Plasmid_v1.1', count_files_extension='.tsv.gz'):
        self.dir = data_dir
        self.plasmid = plasmid
        self.count_files_extension = count_files_extension

        self.manifest = self.get_manifest()
        self.raw_counts = self.get_rawcounts()
        self.fold_changes = self.get_foldchanges()

    def get_library(self, dfile='KY_Library_v1.1_annotated.csv'):
        return pd.read_csv(f'{self.dir}/{dfile}', index_col=0)

    def get_manifest(self, dfile='2018-12-10_to_2018-12-16_CanPipe.xlsx', set_index='Sample_Name', shorten=True):
        sample_name_map = self.get_file_sample_name_map().reset_index()
        sample_name_map.columns = ['file', 'name']
        sample_name_map.index = sample_name_map['file'].apply(lambda v: v.split('.')[0]).values

        manifest = pd.read_excel(f'{self.dir}/{dfile}')
        manifest['Sample_File'] = sample_name_map.loc[manifest['Sample'], 'file'].values
        manifest['Sample_Name'] = sample_name_map.loc[manifest['Sample'], 'name'].values

        manifest['Day'] = manifest['Sample'].apply(lambda v: int(re.findall('.*_([0-9]+)_DAYS', v)[0])).values

        manifest['Replicate'] = manifest['Sample'].apply(lambda v: int(re.findall('.*CRISPR_([0-9]+)_.*', v)[0])).values

        manifest['Cell_line'] = manifest['Sample'].apply(lambda v: v.split('_')[0]).values

        manifest['Condition'] = manifest['Sample'].apply(lambda v: re.findall('.*CRISPR_[0-9]+_(.*)', v)[0].split('_')[0]).values
        manifest['Condition'] = manifest['Condition'].replace('7', 'START').values

        manifest['Name'] = [
            f"{c} Day{int(d)} Rep{int(r)}" if str(d) != 'nan' else self.plasmid for d, r, c in manifest[['Day', 'Replicate', 'Condition']].values
        ]

        if set_index is not None:
            manifest = manifest.dropna(subset=[set_index]).set_index(set_index)

        if shorten:
            short_columns = [
                'ProjectID', 'Day', 'Replicate', 'Condition', 'Cell_line', 'Sample', 'Sample_File', 'Name',
            ]

            manifest = manifest[short_columns]

        return manifest

    def get_file_sample_name_map(self):
        return pd.Series({
            f: pd.read_csv(f'{self.dir}/{f}', index_col=0, sep='\t').columns[1] for f in self.get_count_files()
        })

    def get_count_files(self):
        return [f for f in os.listdir(self.dir) if f.endswith(self.count_files_extension)]

    def get_plasmid_raw_counts(self):
        plasmid_counts = pd.DataFrame([
            pd.read_csv(f'{self.dir}/{f}', index_col=0, sep='\t')[self.plasmid] for f in self.get_count_files()
        ]).T

        assert sum(plasmid_counts.std(1) == 0), 'Not all plasmid are the same'

        return plasmid_counts.iloc[:, 0]

    def get_rawcounts(self, add_plasmid=True):
        raw_counts = pd.DataFrame([
            pd.read_csv(f'{self.dir}/{f}', index_col=0, sep='\t').iloc[:, 1] for f in self.get_count_files()
        ]).T

        if add_plasmid:
            raw_counts = pd.concat([raw_counts, self.get_plasmid_raw_counts()], axis=1, sort=False)

        return raw_counts

    def get_foldchanges(self):
        fcs_gene = {}

        for s in self.manifest[self.manifest['Condition'] != 'DOXY'].index:
            print(f'[INFO] Sample: {s}')

            rawcounts = self.raw_counts[[s, self.plasmid]]

            s_crispy = cy.Crispy(raw_counts=rawcounts, library=cy.Utils.get_crispr_lib(), plasmid=self.plasmid)
            fcs_gene[s] = s_crispy.gene_fold_changes(qc_replicates_thres=None)

        fcs_gene = pd.DataFrame(fcs_gene)

        return fcs_gene


class DataAnalysis(CrispyPlot):
    ORDER = [
        'Plasmid_v1.1',
        'START Day7 Rep1', 'START Day7 Rep2',
        'CTRL Day25 Rep1', 'CTRL Day30 Rep1', 'CTRL Day30 Rep2', 'CTRL Day35 Rep1', 'CTRL Day35 Rep2',
        'DOXY Day25 Rep2', 'DOXY Day30 Rep1', 'DOXY Day30 Rep2', 'DOXY Day35 Rep1', 'DOXY Day35 Rep2',
    ]

    @classmethod
    def rawcounts_total_barplot(cls, dimport):
        plot_df = pd.concat([
            dimport.raw_counts.sum().rename('Total reads'), dimport.manifest
        ], axis=1, sort=False)

        sns.barplot(x='Total reads', y='Name', data=plot_df, color=cls.PAL_DBGD[0], order=cls.ORDER)

        plt.axvline(plot_df['Total reads'].median(), ls='--', lw=0.3, color=cls.PAL_DBGD[1], zorder=1)

        plt.title('Total raw counts')
        plt.ylabel('')

        plt.gcf().set_size_inches(2, 2)
        plt.savefig(f'reports/rescue/rawcounts_total_barplot.pdf', bbox_inches='tight', transparent=True)
        plt.close('all')

    @classmethod
    def rawcounts_greater_than_barplot(cls, dimport, count_thres=10):
        plot_df = pd.concat([
            (dimport.raw_counts > count_thres).sum().rename('total'), dimport.manifest
        ], axis=1, sort=False)

        sns.barplot(x='total', y='Name', data=plot_df, color=cls.PAL_DBGD[0], order=cls.ORDER)

        plt.axvline(plot_df['total'].median(), ls='--', lw=0.3, color=cls.PAL_DBGD[1], zorder=1)

        plt.title(f'sgRNAs with counts > {count_thres}')
        plt.ylabel('Number of sgRNAs')

        plt.gcf().set_size_inches(2, 2)
        plt.savefig(f'reports/rescue/rawcounts_threshold_barplot.pdf', bbox_inches='tight', transparent=True)
        plt.close('all')

    @classmethod
    def rawcounts_scatter(cls, dimport, sample):
        day, rep, cond = dimport.manifest.loc[sample, ['Day', 'Replicate', 'Condition']]
        condition = f'{cond} Day{day} Rep{rep}'

        plot_df = pd.concat([
            dimport.raw_counts[dimport.plasmid].rename('plasmid'), dimport.raw_counts[sample].rename('sample')
        ], axis=1, sort=False)
        plot_df = plot_df[(plot_df > 1).sum(1) == 2]
        plot_df = np.log10(plot_df)

        plt.scatter(plot_df['plasmid'], plot_df['sample'], color=cls.PAL_DBGD[0])

        plt.xlabel(f'{dimport.plasmid}\nraw counts (log10)')
        plt.ylabel(f'{condition}\nraw counts (log10)')

        lims = [plot_df.min().min(), plot_df.max().max()]
        plt.xlim(lims)
        plt.ylim(lims)

        plt.gcf().set_size_inches(2, 2)
        plt.savefig(f'reports/rescue/rawcounts_scatter_{condition}.png', bbox_inches='tight', dpi=600)
        plt.close('all')

    @classmethod
    def foldchange_clustermap(cls, dimport):
        plot_df = dimport.fold_changes.rename(columns=dimport.manifest['Name'])

        sns.clustermap(plot_df.corr(), cmap='RdYlBu', center=0)
        plt.gcf().set_size_inches(3, 3)
        plt.savefig(f'reports/rescue/foldchanges_clustermap.pdf', bbox_inches='tight', dpi=600)
        plt.close('all')

    @classmethod
    def qc_essential(cls, dimport):
        plot_df = dimport.fold_changes.copy().rename(columns=dimport.manifest['Name'])

        cy.QCplot.plot_cumsum_auc(plot_df, cy.Utils.get_essential_genes())

        plt.gcf().set_size_inches(3, 3)
        plt.savefig(f'reports/rescue/qc_essential.pdf', bbox_inches='tight', dpi=600)
        plt.close('all')


if __name__ == '__main__':
    dimport = DataImporter()

    #
    headers = dimport.manifest['Name'].apply(lambda v: v.replace(' ', '.'))

    raw_counts = dimport.raw_counts.rename(columns=headers)
    raw_counts['gene'] = dimport.get_library().loc[raw_counts.index]['GENES'].values
    raw_counts = raw_counts.reset_index()
    raw_counts = raw_counts[['sgRNA', 'gene'] + list(headers.values) + [dimport.plasmid]]
    raw_counts = raw_counts.dropna()
    raw_counts.to_csv('data/rescue/mageck/rescue_rawcounts.txt', sep='\t', index=False)

    #
    fcs_gene = {}
    for s in dimport.manifest[(dimport.manifest['Condition'] == 'DOXY') & (dimport.manifest['Day'] != 25)].index:
        rawcounts = dimport.raw_counts[[s, dimport.plasmid]]
        rawcounts = rawcounts[rawcounts[s] > 30]

        s_crispy = cy.Crispy(raw_counts=rawcounts, library=cy.Utils.get_crispr_lib(), plasmid=dimport.plasmid)
        fcs_gene[s] = s_crispy.fold_changes(qc_replicates_thres=None)
    fcs_gene = pd.DataFrame(fcs_gene)

    fc_doxy_30 = fcs_gene[dimport.manifest.query("(Condition == 'DOXY') & (Day == 30)").index].dropna().mean(1)
    fc_doxy_30 = fc_doxy_30.groupby(dimport.get_library().loc[fc_doxy_30.index]['GENES']).mean()

    fc_doxy_35 = fcs_gene[dimport.manifest.query("(Condition == 'DOXY') & (Day == 35)").index].dropna().mean(1)
    fc_doxy_35 = fc_doxy_35.groupby(dimport.get_library().loc[fc_doxy_35.index]['GENES']).mean()

    plot_df = pd.concat([fc_doxy_30.rename('DOXY_Day30'), fc_doxy_35.rename('DOXY_Day35')], axis=1, sort=False).dropna()

    plot_df.eval('DOXY_Day30 - DOXY_Day35').sort_values()

    plot_df = pd.concat([fcs_gene.dropna().median(1).rename('median'), fcs_gene.dropna().std(1).rename('std')], axis=1).dropna()

    plot_df['median'].groupby(dimport.get_library().loc[plot_df.index]['GENES']).mean().sort_values().to_clipboard()

    plot_df.query('std < 3').sort_values('median').tail(60)

    sns.jointplot('median', 'std', data=plot_df)
    plt.show()

    #
    crtl_samples = [
        'EGAN00001904711.sample', 'EGAN00001904713.sample'
    ]

    fcs_crtl = []
    for i, crtl in enumerate(crtl_samples):
        rawcounts = dimport.raw_counts[[crtl, dimport.plasmid]]
        rawcounts = rawcounts[rawcounts[crtl] > 30]

        crtl_crispy = cy.Crispy(raw_counts=rawcounts, library=cy.Utils.get_crispr_lib(), plasmid=dimport.plasmid)
        crtl_crispy_fcs = crtl_crispy.fold_changes(qc_replicates_thres=None).rename(f'replicate_{i+1}')

        fcs_crtl.append(crtl_crispy_fcs)

    fcs_crtl = pd.DataFrame(fcs_crtl).T
    fcs_crtl = fcs_crtl.groupby(dimport.get_library().loc[fcs_crtl.index]['GENES']).mean()

    g = sns.JointGrid(data=fcs_crtl, x='replicate_1', y='replicate_2')

    g.plot_joint(plt.scatter, color=cy.QCplot.PAL_DBGD[0], s=40, edgecolor='white', alpha=.5)

    g = g.annotate(pearsonr)

    plt.gcf().set_size_inches(3, 3)
    plt.savefig(f'reports/rescue/crtl_replicate_corrplot_gene.pdf', bbox_inches='tight', dpi=600)
    plt.close('all')

    #
    doxy_samples = [
        'EGAN00001904712.sample', 'EGAN00001904714.sample'
    ]

    fcs_doxy = []
    for i, doxy in enumerate(doxy_samples):
        rawcounts = dimport.raw_counts[[doxy, dimport.plasmid]]
        rawcounts = rawcounts[rawcounts[doxy] > 30]

        doxy_crispy = cy.Crispy(raw_counts=rawcounts, library=cy.Utils.get_crispr_lib(), plasmid=dimport.plasmid)
        doxy_crispy_fcs = doxy_crispy.fold_changes(qc_replicates_thres=None).rename(f'replicate_{i+1}')

        fcs_doxy.append(doxy_crispy_fcs)

    fcs_doxy = pd.DataFrame(fcs_doxy).T
    fcs_doxy = fcs_doxy.groupby(dimport.get_library().loc[fcs_doxy.index]['GENES']).mean()

    g = sns.JointGrid(data=fcs_doxy, x='replicate_1', y='replicate_2')

    g.plot_joint(plt.scatter, color=cy.QCplot.PAL_DBGD[0], s=40, edgecolor='white', alpha=.5)

    g = g.annotate(pearsonr)

    plt.gcf().set_size_inches(3, 3)
    plt.savefig(f'reports/rescue/doxy_replicate_corrplot_gene.pdf', bbox_inches='tight', dpi=600)
    plt.close('all')

    #
    plot_df = pd.concat([fcs_crtl, fcs_doxy.mean(1).rename('doxy')], axis=1, sort=False).dropna()

    sns.jointplot('replicate_2', 'doxy', data=plot_df)
    plt.show()

    plot_df.query('doxy > 2')
