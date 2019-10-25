import ast
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from crispy.Bedit import CytidineBaseEditor, AdenineBaseEditor, BeditPlot, Modifications


def filter_offtarget(glib, max_offtarget=1):
    return glib[[ast.literal_eval(goff)[0] == max_offtarget for goff in glib['off_target_summary']]]


if __name__ == '__main__':
    ppdir = '/Users/eg14/Data/resources/phosphositeplus/'

    reg_phospho = pd.read_csv(f'{ppdir}/Phosphorylation_site_dataset.txt', sep='\t', skiprows=3)\
        .query("ORGANISM == 'human'")

    reg_acetyl = pd.read_csv(f'{ppdir}/Acetylation_site_dataset.txt', sep='\t', skiprows=3)\
        .query("ORGANISM == 'human'")

    reg_methy = pd.read_csv(f'{ppdir}/Methylation_site_dataset.txt', sep='\t', skiprows=3)\
        .query("ORGANISM == 'human'")

    reg_sumoy = pd.read_csv(f'{ppdir}/Sumoylation_site_dataset.txt', sep='\t', skiprows=3)\
        .query("ORGANISM == 'human'")

    # -
    dfile = 'reports/bedit/WGE_JAK1_guides.tsv'

    glib = pd.read_csv(dfile, sep='\t')
    glib = filter_offtarget(glib)

    gene_strand = '-'

    info_columns = ['strand', 'gRNA', 'off_target_summary', 'location']

    edits, single_edits = [], []
    bec, bea = CytidineBaseEditor(), AdenineBaseEditor()
    for strand, guide, offtarget, location in glib[info_columns].values:
        for be in [bec, bea]:
            chrm, start, end = be.parse_coordinates(location)
            guide_edited = be.edit_guide(guide, strand, gene_strand)

            print(f'# {be.name}, {chrm}:{start}-{end}:')
            print(f'Guide strand: {strand}, Gene strand: {gene_strand}')

            be.print_guide(guide)
            be.print_guide(guide_edited)

            guide_edits = be.to_vep(guide, guide_edited)

            if guide_edits is not None:
                guide_vep = dict(
                    chr=chrm,
                    start=start + guide_edits[1],
                    end=start + guide_edits[2],
                    edit=guide_edits[0],
                    strand='-'
                )
                edits.append(guide_vep)
                print(guide_vep)

                for bp, i in be.list_base_edits(guide, guide_edited):
                    single_edits.append(dict(chr=chrm, pos=start + i, edit=bp, be=be.name))

        print('\n')

    # -
    single_edits = pd.DataFrame(single_edits)

    # -
    edits_df = pd.DataFrame(edits)[['chr', 'start', 'end', 'edit', 'strand']]
    edits_df.to_csv('reports/bedit/WGE_JAK1_vep_input.txt', sep='\t', index=False, header=False)

    # -
    vep = pd.read_csv('reports/bedit/WGE_JAK1_vep_output.txt', sep='\t')
    vep = vep[vep['CSN'].apply(lambda v: v.startswith('ENST00000342505.4'))]

    vep = vep.dropna(subset=['Amino_acids'])
    vep = vep[vep['Amino_acids'] != '-']

    #
    plot_df = vep.copy()
    plot_df = plot_df[plot_df['Amino_acids'].apply(lambda v: '/' in v)]
    plot_df = plot_df[plot_df['Amino_acids'].apply(lambda v: len(v) == 3)]

    plot_df['wildtype'] = plot_df['Amino_acids'].apply(lambda v: v.split('/')[0]).replace(Modifications.get_names())
    plot_df['mutant'] = plot_df['Amino_acids'].apply(lambda v: v.split('/')[1]).replace(Modifications.get_names())

    BeditPlot.aa_grid(plot_df)
    plt.gcf().set_size_inches(6.5, 6.5)
    plt.savefig(f'reports/bedit/aa_grid_jak1.pdf', bbox_inches='tight', transparent=True)
    plt.close('all')

    #
    aa_alts = []
    for aae, pos in vep[['Amino_acids', 'Protein_position']].values:
        if '/' in aae:
            start = int(pos.split('-')[0])
            original, edited = aae.split('/')

            for i, aa in enumerate(original):
                if original[i] != edited[i]:
                    aa_alternation = dict(
                        original=original[i],
                        edited=edited[i],
                        edit=f'{original[i]} > {edited[i]}',
                        pos=start + i
                    )
                    print(aa_alternation)
                    aa_alts.append(aa_alternation)
    aa_alts = pd.DataFrame(aa_alts)

    #
    ptms = vep[vep['Amino_acids'].apply(lambda v: '/' in v)]

    ptms['site'] = \
        ptms['Amino_acids'].apply(lambda v: v[0]) + \
        ptms['Protein_position'].astype(str)

    ptms['residue'] = \
        ptms['Amino_acids'].apply(lambda v: v[0]) + \
        ptms['Protein_position'].astype(str) + \
        ptms['Amino_acids'].apply(lambda v: v[-1:])

    #
    sift = ptms['SIFT'].apply(lambda v: v.split('(')[0]).value_counts()
    pholyphen = ptms['PolyPhen'].apply(lambda v: v.split('(')[0]).value_counts()
    consequence = pd.Series([i for i in ptms['Consequence'] if ',' not in i]).value_counts()

    #
    phosphosites = aa_alts[[i[0] in ['S', 'T', 'Y'] for i in aa_alts['original']]]
    acetylation = aa_alts[[i[0] in ['K'] for i in aa_alts['original']]]
    methylation = aa_alts[[i[0] in ['K', 'R'] for i in aa_alts['original']]]
