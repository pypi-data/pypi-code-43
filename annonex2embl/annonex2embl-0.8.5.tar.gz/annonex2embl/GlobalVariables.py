#!/usr/bin/env python
'''
Setting global variables.
'''

###############
# AUTHOR INFO #
###############

__author__ = 'Michael Gruenstaeudl <m.gruenstaeudl@fu-berlin.de>'
__copyright__ = 'Copyright (C) 2016-2019 Michael Gruenstaeudl'
__info__ = 'annonex2embl'
__version__ = '2019.10.16.1700'

#############
# DEBUGGING #
#############

#import ipdb
#ipdb.set_trace()

#########
# OTHER #
#########

# Valid start codon as defined by [...]
# http://
#global nex2ena_start_codon
nex2ena_start_codon = 'ATG'

# Valid stop codons as defined by [...]
# http://
#global nex2ena_stop_codons
nex2ena_stop_codons = ['TAG', 'TAA', 'TGA']  # amber, ochre, opal

# Valid sequence topology as defined by the EMBL User Manual
# (Chapter 3.4.1).
# ftp://ftp.ebi.ac.uk/pub/databases/embl/doc/usrman.txt
#global nex2ena_valid_topologies
nex2ena_valid_topologies = ['linear', 'circular']

# Valid taxonomic divisions as defined by the EMBL User Manual
# (Chapter 3.2).
# ftp://ftp.ebi.ac.uk/pub/databases/embl/doc/usrman.txt
#global nex2ena_valid_tax_divisions
nex2ena_valid_tax_divisions = [
    'PHG', 'ENV', 'FUN', 'HUM', 'INV', 'MAM', 'VRT', 'MUS',
    'PLN', 'PRO', 'ROD', 'SYN', 'TGN', 'UNC', 'VRL', 'XXX']
#    See Section '3.2 Taxonomic Division' in EMBL User Manual
#        Division                 Code
#        -----------------        ----
#        Bacteriophage            PHG
#        Environmental Sample     ENV
#        Fungal                   FUN
#        Human                    HUM
#        Invertebrate             INV
#        Other Mammal             MAM
#        Other Vertebrate         VRT
#        Mus musculus             MUS
#        Plant                    PLN
#        Prokaryote               PRO
#        Other Rodent             ROD
#        Synthetic                SYN
#        Transgenic               TGN
#        Unclassified             UNC (i.e. unknown)
#        Viral                    VRL
#        ENA SUBMISSIONS          XXX


# Valid feature table qualifiers as defined by the International
# Nucleotide Sequence Database Collection (INSDC)
# http://www.insdc.org/files/feature_table.html#7.3.1
#global nex2ena_valid_INSDC_quals
nex2ena_valid_INSDC_quals = [
    'allele', 'altitude', 'anticodon', 'artificial_location',
    'bio_material', 'bound_moiety', 'cell_line', 'cell_type',
    'chromosome', 'citation', 'clone', 'clone_lib', 'codon_start',
    'collected_by', 'collection_date', 'compare', 'country',
    'cultivar', 'culture_collection', 'db_xref', 'dev_stage',
    'direction', 'EC_number', 'ecotype', 'environmental_sample',
    'estimated_length', 'exception', 'experiment', 'focus',
    'frequency', 'function', 'gap_type', 'gene', 'gene_synonym',
    'germline', 'haplogroup', 'haplotype', 'host', 'identified_by',
    'inference', 'isolate', 'isolation_source', 'lab_host',
    'lat_lon', 'linkage_evidence', 'locus_tag', 'macronuclear',
    'map', 'mating_type', 'mobile_element_type', 'mod_base',
    'mol_type', 'ncRNA_class', 'note', 'number', 'old_locus_tag',
    'operon', 'organelle', 'organism', 'partial', 'PCR_conditions',
    'PCR_primers', 'phenotype', 'plasmid', 'pop_variant', 'product',
    'protein_id', 'proviral', 'pseudo', 'pseudogene', 'rearranged',
    'regulatory_class', 'replace', 'ribosomal_slippage',
    'rpt_family', 'rpt_type', 'rpt_unit_range', 'rpt_unit_seq',
    'satellite', 'segment', 'serotype', 'serovar', 'sex',
    'specimen_voucher', 'standard_name', 'strain', 'sub_clone',
    'sub_species', 'sub_strain', 'tag_peptide', 'tissue_lib',
    'tissue_type', 'transgenic', 'translation', 'transl_except',
    'transl_table', 'trans_splicing', 'type_material', 'variety']

# Valid feature table qualifiers as defined by the International
# Nucleotide Sequence Database Collection (INSDC)
# http://www.insdc.org/files/feature_table.html#7.3.1
#global nex2ena_valid_INSDC_featurekeys
nex2ena_valid_INSDC_featurekeys = [
    'assembly_gap', 'C_region', 'CDS', 'centromere',
    'D-loop', 'D_segment', 'exon', 'gap', 'gene', 'iDNA',
    'intron', 'J_segment', 'LTR', 'mat_peptide', 'misc_binding',
    'misc_difference', 'misc_feature', 'misc_recomb', 'misc_RNA',
    'misc_structure', 'mobile_element', 'modified_base', 'mRNA',
    'ncRNA', 'N_region', 'old_sequence', 'operon', 'oriT',
    'polyA_site', 'precursor_RNA', 'prim_transcript', 'primer_bind',
    'protein_bind', 'regulatory', 'repeat_region', 'rep_origin',
    'rRNA', 'S_region', 'sig_peptide', 'source', 'stem_loop',
    'STS', 'telomere', 'tmRNA', 'transit_peptide', 'tRNA',
    'unsure', 'V_region', 'V_segment', 'variation', "3'UTR", "5'UTR",
    "IGS"]

# Valid organelle qualifiers as defined by the International
# Nucleotide Sequence Database Collection (INSDC)
# http://www.insdc.org/files/feature_table.html#7.3.1
#global nex2ena_valid_INSDC_organelle
nex2ena_valid_INSDC_organelle = [
    'chromatophore', 'hydrogenosome', 'mitochondrion', 'nucleomorph',
    'plastid', 'mitochondrion:kinetoplast', 'plastid:chloroplast',
    'plastid:apicoplast', 'plastid:chromoplast', 'plastid:cyanelle',
    'plastid:leucoplast', 'plastid:proplastid']

nex2ena_valid_orientations = [
    'forw','rev']
