#!/usr/bin/env python
'''
Custom operations for EMBL submission preparation tool
'''

#####################
# IMPORT OPERATIONS #
#####################

import GlobalVariables as GlobVars

from operator import itemgetter
from itertools import groupby
from Bio import SeqFeature
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import ExactPosition, FeatureLocation, CompoundLocation

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

###########
# CLASSES #
###########

class GenerateFeatLoc:
    ''' This class contains functions to generate or manipulate
        SeqFeature location objects.
    '''

    def __init__(self):
        pass

    @staticmethod
    def _exact(csrange):
        ''' An internal static function to generate an exact feature
            location. '''
        start_pos = csrange[0]
        stop_pos = csrange[-1] + 1
        start_exact = ExactPosition(start_pos)
        stop_exact = ExactPosition(stop_pos)
        return FeatureLocation(start_exact, stop_exact)

    @staticmethod
    def _extract_contiguous_subsets(compound_integer_range):
        ''' An internal static function to extract all contiguous
            integer ranges from compound integer range.
        '''
#        Examples:
#            Example 1:
#            >>> compound_integer_range = [1,2,3,7,8,9]
#            >>> _extract_contiguous_subsets(compound_integer_range)
#            Out: [[1, 2, 3], [7, 8, 9]]

        outlist = []
        for k, g in groupby(enumerate(compound_integer_range),
                            lambda i_x: i_x[0] - i_x[1]):
            outlist.append(list(map(itemgetter(1), g)))
        return outlist

    def make_location(self, charset_range):
        ''' This function goes through a decision tree and generates
            fitting feature locations.
        Args:
            charset_range (list): a list of index positions, example: [1,2,3,8,9 ...]
        Returns:
            FeatureLocation (obj):  A SeqFeature location object; either a
                                    FeatureLocation or a CompoundLocation
        Raises:
            -
        '''
        contiguous_ranges = GenerateFeatLoc._extract_contiguous_subsets(
            charset_range)
        # Convert each contiguous range into an exact feature location
        for countr, rnge in enumerate(contiguous_ranges):
            contiguous_ranges[countr] = GenerateFeatLoc._exact(rnge)
        if len(contiguous_ranges) > 1:
            return CompoundLocation(contiguous_ranges)
        else:
            return contiguous_ranges[0]

    def make_location_complement(self, location_object):
        location_object._set_strand(-1)
        return location_object

    def make_start_fuzzy(self, location_object):
        ''' This function makes the start position of location
            objects fuzzy.
        '''
        orient = location_object._get_strand()
        if hasattr(location_object, 'parts'):
            if len(location_object.parts) == 1:
                if orient == -1:  # If feature reverse, fuzzy start must change with it
                    new_start_pos = SeqFeature.BeforePosition(
                        location_object.end)
                    location_object = SeqFeature.FeatureLocation(
                        location_object.start, new_start_pos)
                else:
                    new_start_pos = SeqFeature.BeforePosition(
                        location_object.start)
                    location_object = SeqFeature.FeatureLocation(
                        new_start_pos, location_object.end)
            if len(location_object.parts) > 1:
                if orient == -1:
                    new_start_pos = SeqFeature.BeforePosition(
                        location_object.parts[0].end)
                    location_object.parts[0] = SeqFeature.FeatureLocation(
                        location_object.parts[0].start, new_start_pos)
                else:
                    new_start_pos = SeqFeature.BeforePosition(
                        location_object.parts[0].start)
                    location_object.parts[0] = SeqFeature.FeatureLocation(
                        new_start_pos, location_object.parts[0].end)
        location_object._set_strand(orient)
        return location_object

    def make_end_fuzzy(self, location_object):
        ''' This function makes the end position of location
            objects fuzzy.
        '''

#        Examples:
#            Example 1:
#                >>> from Bio import SeqFeature
#                >>> start_pos = SeqFeature.ExactPosition(5)
#                >>> end_pos = SeqFeature.ExactPosition(9)
#                >>> location_object = SeqFeature.FeatureLocation(start_pos, end_pos)
#                >>> location_object
#                Out: FeatureLocation(ExactPosition(5), ExactPosition(9))
#                >>> new_loc = GenerateFeatLoc().make_end_fuzzy(location_object)
#                >>> new_loc
#                Out: FeatureLocation(ExactPosition(5), AfterPosition(9))
#
#            Example 2:
#                >>> from Bio import SeqFeature
#                >>> csrange = [1,2,3,7,8]
#                >>> location_object = GenerateFeatLoc().make_location(csrange)
#                >>> location_object
#                Out: CompoundLocation([FeatureLocation(ExactPosition(1),
#                ExactPosition(4)), FeatureLocation(ExactPosition(7),
#                ExactPosition(9))], 'join')
#                >>> new_loc = GenerateFeatLoc().make_end_fuzzy(location_object)
#                >>> new_loc
# Out: CompoundLocation([FeatureLocation(ExactPosition(1),
# ExactPosition(4)), FeatureLocation(ExactPosition(7), AfterPosition(9))],
# 'join')
        orient = location_object._get_strand()
        if hasattr(location_object, 'parts'):
            if len(location_object.parts) == 1:
                if orient == -1: # If feature reverse, fuzzy end must change with it
                    new_end_pos = SeqFeature.BeforePosition(location_object.start)
                    location_object = SeqFeature.FeatureLocation(
                        new_end_pos, location_object.end)
                else:
                    new_end_pos = SeqFeature.AfterPosition(location_object.end)
                    location_object = SeqFeature.FeatureLocation(
                        location_object.start, new_end_pos)
            if len(location_object.parts) > 1:
                if orient == -1:
                    new_end_pos = SeqFeature.BeforePosition(
                        location_object.parts[-1].start)
                    location_object.parts[-1] = SeqFeature.FeatureLocation(
                        new_end_pos, location_object.parts[-1].end)
                else:
                    new_end_pos = SeqFeature.AfterPosition(
                        location_object.parts[-1].end)
                    location_object.parts[-1] = SeqFeature.FeatureLocation(
                        location_object.parts[-1].start, new_end_pos)
        location_object._set_strand(orient)

        return location_object


class GenerateSeqFeature:
    ''' This class contains functions to generate SeqFeatures. '''

    def __init__(self):
        pass

    def source_feat(self, full_len, quals, charset_names):
        ''' This function generates the SeqFeature source for a
            SeqRecord. The SeqFeature source is critical for
            submissions to EMBL or GenBank, as it contains all the
            relevant info on collection locality, herbarium voucher,
            etc. It also provides info on which translation table is
            used if a CDS sequence feature is encountered among the
            gene names.
        Args:
            full_len (int): the full length of the seq in question;
                            example: 509
            quals (dict):   a dictionary of qualifiers; example:
                            {'isolate': 'taxon_B', 'country': 'Ecuador'}
            charset_names (list): a list of gene names; example:
                            ['foo_gene', 'foo_CDS']
        Returns:
            SeqFeature (obj):   A SeqFeature object
        Raises:
            [currently nothing]
        '''
        full_index = list(range(0, full_len))
        feature_loc = GenerateFeatLoc().make_location(full_index)
        quals['mol_type'] = "genomic DNA"
        source_feature = SeqFeature.SeqFeature(
            feature_loc,
            id='source',
            type='source',
            qualifiers=quals)
        return source_feature

    def regular_feat(self, feature_name, feature_type, feature_orient, feature_loc,
                     transl_table, feature_seq, feature_product=None):
        ''' This function generates a regular SeqFeature for a SeqRecord.
        Args:
            feature_name (str):  usually a gene symbol; example: 'matK'
            feature_type (str):  an identifier as to the type of feature;
                                 example: 'intron'
            feature_orient (str): a string defining
            feature_loc (object): a SeqFeature object specifying a simple
                                  or compund location on a DNA string
            transl_table (int): an integer; example: 11 (for bacterial code)
            feature_product (str): the product of the feature in question;
                                   example: 'maturase K'
            feature_seq (str): nucleotide sequence sequence
        Returns:
            SeqFeature (obj):   A SeqFeature object
        Raises:
            -
        '''
        # 1. Define the annotation type
        if feature_type not in GlobVars.nex2ena_valid_INSDC_featurekeys:
            msg = '%s nex2embl ERROR: Internal error: '\
                  'Name of feature key not passed correctly.'
            warnings.warn(msg)
            raise Exception
        # 2. Generate qualifiers
        quals = {}
        if feature_name:
            quals = {'note': feature_name}
        # 3. If a coding feature, add special qualifiers
        if feature_product:
            if feature_type == 'CDS' or feature_type == 'gene':
                quals['product'] = feature_product
        if feature_type == 'CDS':
            quals['transl_table'] = transl_table
            # Add a function to add "/codon_start=1" in CDS feature,
            # if start and stop position of feature is uncertain
            # (i.e., <100..>200).
            if (not feature_seq.startswith(GlobVars.nex2ena_start_codon)) or (all([not feature_seq.endswith(c) for c in GlobVars.nex2ena_stop_codons])):
                quals['codon_start'] = 1
        if feature_type == 'gap':
            quals['estimated_length'] = str(feature_loc.end.position-feature_loc.start.position)
            #quals['estimated_length'] = str(feature_loc.end.real-feature_loc.start.real+1)
        # 4. Add a function to read in if a charset is forward or reverse and to adjust the info in the feature table.
        if feature_orient == "forw":
            feature_orient = 1
        else:
            feature_orient = -1
        seq_feature = SeqFeature.SeqFeature(
            feature_loc,
            id=feature_name,
            type=feature_type,
            strand=feature_orient,
            qualifiers=quals)
        return seq_feature




class GenerateSeqRecord:
    ''' This class contains functions to generate SeqRecords. '''

    def __init__(self):
        pass

    def base_record(self, current_seq, current_qual, uniq_seqid_col,
                    seq_version, descr_DEline, topology, tax_division,
                    organelle):
        ''' This function generates a base SeqRecord (i.e., the foundation to
            subsequent SeqRecords).
        Args:
            current_seq (str): the DNA sequence of; example: 1
            current_qual (xxx): foobar; example: foobar
            uniq_seqid_col (str): the column label of the .csv-file that
                                  contains info on the sequence names;
                                  example: "isolate"
            seq_version (str):    an integer in string format
            descr_DEline (str):   a text string to be included in the
                                  DE line
            topology (str):       one of the valid ENA topology
                                  specifications
            tax_division (str):   one of the valid ENA taxonomic
                                  divisions
            organelle (str):      one of the valid INDSC organelle
                                  descriptors
        Returns:
            SeqRecord (obj):      A SeqRecord object
        '''
        # 1. Selecting correct sequence line
        uniq_seqid = current_qual[uniq_seqid_col]
        # 2. Generating parse-able ID line
        ID_line = uniq_seqid + '.' + seq_version
        # Note to line above: seq_version is parsed internally from
        # ID-line when EMBL format is written
        try:
            org_name = current_qual['organism']
        except Exception:
            org_name = 'undetermined organism'
        # 3. Generating DE line
        descr_DEline = descr_DEline.replace('"', '')
        DE_line = ' '.join([org_name, descr_DEline + ',', 'isolate',
                            uniq_seqid])
        # 4. Set up new seq record
        seq_record = SeqRecord(current_seq, id=ID_line, name=org_name,
                               description=DE_line)
        # 5. Specify the topology of the sequence
        if topology in GlobVars.nex2ena_valid_topologies:
            seq_record.annotations['topology'] = topology
        #else:
        #    seq_record.annotations['topology'] = 'linear'
        # 6. Add ID line info on 'taxonomic division'
        if tax_division in GlobVars.nex2ena_valid_tax_divisions:
            seq_record.annotations['data_file_division'] = tax_division
        #else:
        #    seq_record.annotations['data_file_division'] = 'UNC'
        # 7. Specify the organelle of the sequence
        if organelle in GlobVars.nex2ena_valid_INSDC_organelle:
            seq_record.annotations['organelle'] = organelle
        return seq_record
