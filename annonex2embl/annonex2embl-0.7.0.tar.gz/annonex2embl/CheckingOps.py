#!/usr/bin/env python
'''
Custom operations to check annotations
'''

#####################
# IMPORT OPERATIONS #
#####################

import GenerationOps as GnOps
import GlobalVariables as GlobVars
import warnings

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import FeatureLocation
from Bio.SeqFeature import CompoundLocation
from unidecode import unidecode
from itertools import chain

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

class AnnoCheck:
    ''' This class contains functions to evaluate the quality of an
        annotation.
    Args:
        extract (obj):      a sequence object; example: Seq('ATGGAGTAA',
                            IUPACAmbiguousDNA())
        feature_object (obj):   a feature object
        record_id (str):    a string deatiling the name of the sequence in
                            question; example: "taxon_A"
        transl_table (int): an integer; example: 11 (for bacterial code)
    Returns:
        tupl.   The return consists of the translated sequence (a str)
                and the updated feature location (a location object);
                example: (transl_out, feat_loc)
    Raises:
        Exception
    '''

    def __init__(self, extract, feature, record_id, transl_table=11):
        self.extract = extract
        self.feature = feature
        self.record_id = record_id
        self.transl_table = transl_table

    @staticmethod
    def _transl(extract, transl_table, to_stop=False, cds=False):
        ''' An internal static function to translate a coding region. '''
        
        with warnings.catch_warnings():  # Note: Suppressing warnings necessary to suppress the Biopython warning about an annotation not being a multiple of three
            warnings.filterwarnings("ignore")
            transl = extract.translate(table=transl_table, to_stop=to_stop,
                                       cds=cds)
            # Adjustment for non-start codons given the necessary use of
            # cds=True in TPL.
            if not extract.startswith(GlobVars.nex2ena_start_codon):
                first_codon_seq = extract[0:3]
                first_aa = first_codon_seq.translate(table=transl_table,
                                                     to_stop=to_stop, cds=False)
                transl = first_aa + transl[1:]
        return transl

    @staticmethod
    def _check_protein_start(extract, transl_table):
        ''' An internal static function to translate a coding region and check
            if it starts with a methionine. '''
        transl = extract.translate(table=transl_table)
        return transl.startswith('M')

    @staticmethod
    def _adjust_feat_loc(location_object, transl_with_internStop,
                         transl_without_internStop):
        ''' An internal static function to adjust the feature location if an
            internal stop codon were present. '''
        if len(transl_without_internStop) > len(transl_with_internStop):
            # 1. Unnest the nested lists
            contiguous_subsets = [list(range(e.start.position, e.end.position))
                for e in location_object.parts]
            compound_integer_range = sum(contiguous_subsets, [])
            # 2. Adjust location range
            len_with_internStop = len(transl_with_internStop) * 3
            # IMPORTANT!: In TFL, the "+3" is for the stop codon, which is
            # counted in the location range, but is not part of the AA
            # sequence of the translation.
            adjusted_range = compound_integer_range[:(len_with_internStop+3)]
            # 3. Establish location
            feat_loc = GnOps.GenerateFeatLoc().make_location(adjusted_range)
        if len(transl_without_internStop) == len(transl_with_internStop):
            feat_loc = location_object
        return feat_loc

    def check(self):
        ''' This function performs checks on a coding region.
            Specifically, the function tries to translate the coding
            region (CDS) directly, using the internal checker
            "cds=True". If a direct translation fails, it confirms if
            the CDS starts with a methionine. If the CDS does not start
            with a methionine, a ValueError is raised. If the CDS does
            start with a methionine, translations are conducted with
            and without regard to internal stop codons. The shorter
            of the two translations is kept. The feature location is
            adjusted, where necessary.
        Note:
            The asterisk indicating a stop codon is truncated under
            _transl(to_stop=True) and must consequently be added again
            (see line 137).
        '''
        try:
            # Note: TFL must contain "cds=True"; don't delete it
            transl_out = AnnoCheck._transl(self.extract,
                                           self.transl_table, cds=True)
            feat_loc = self.feature.location
        except:
            try:
                without_internalStop = AnnoCheck._transl(self.extract,
                                                         self.transl_table)
                with_internalStop = AnnoCheck._transl(
                    self.extract, self.transl_table, to_stop=True)
                transl_out = with_internalStop
                feat_loc = AnnoCheck._adjust_feat_loc(
                    self.feature.location, with_internalStop, without_internalStop)
            except Exception:
                msg = 'Translation of feature `%s` of '\
                      'sequence `%s` is unsuccessful.' % (self.feature.id, self.record_id)
                #warnings.warn(msg)
                raise Exception(msg)
        if len(transl_out) < 2:
            msg = 'Translation of feature `%s` of '\
                  'sequence `%s` indicates a protein length of only a '\
                  'single amino acid.' % (self.feature.id, self.record_id)
            #warnings.warn(msg)
            raise Exception(msg)
        # IMPORTANT!!!: In an ENA record, the translation does not display the
        # stop codon (i.e., the '*'), while the feature location range (i.e., 738..2291)
        # very much includes its position, which is biologically logical, as
        # a stop codon is not an amino acid in a translation.
        # Thus, TFL would be incorrect, because it would add back an asterisk into the translation.
        #transl_out = transl_out + "*"
        return (transl_out, feat_loc)

    def for_unittest(self):
        try:
            transl_out, feat_loc = AnnoCheck(
                self.extract, self.feature, self.record_id, self.transl_table).check()
            if isinstance(transl_out, Seq) and isinstance(feat_loc,
                                                          FeatureLocation):
                return True
            return False
        # except ValueError: # Keep 'ValueError'; don't replace with 'Exception'
        #    return False
        except Exception as e:
            print(e)
            raise


class TranslCheck:
    ''' This class contains functions to coordinate different checks. '''

    def __init__(self):
        pass

    # This function extract the sequence from pattern sequence
    # for a forward and reverse strand
    def extract(self, feature, seq_record):
        if feature._get_strand() == 1:
            return feature.extract(seq_record)
        else:
            reverse = SeqRecord("")
            for i in feature.location.parts[::-1]:
                reverse.seq = reverse.seq + i.extract(seq_record).seq
            return reverse

    # By checking the translation of a CDS or an gene it may happen that
    # the location from the CDS or gene had to be adjusted. If after such
    # a feature a IGS or intron follows it have to be adjust aswell.
    # This is done by this function
    def adjustLocation(self, oldLocation, newLocation):
        start = []
        end = []
        start.append(newLocation.end)
        t = oldLocation.start
        for i in oldLocation:
            if not i == t:
                end.append(t)
                start.append(i)
                t = i
            t = t + 1
        end.append(oldLocation.end)
        locations = []
        for i in range(len(start)):
            locations.append(FeatureLocation(start[i],end[i]))
        try:
            return CompoundLocation(locations)
        except Exception as e:
            return locations[0]

    def transl_and_quality_of_transl(self, seq_record, feature, transl_table):
        ''' This function conducts a translation of a coding region and checks
            the quality of said translation.
        Args:
            seq_record (obj):   foobar; example: 'foobar'
            feature (obj):      foobar; example: 'foobar'
            transl_table (int):
        Returns:
            True, unless exception
        Raises:
            feature
        '''
        extract = self.extract(feature, seq_record)
        try:
            transl, loc = AnnoCheck(extract.seq, feature, seq_record.id,
                                    transl_table).check()
            if feature.type == 'CDS':
                feature.qualifiers["translation"] = transl
            if feature.type == 'exon' or feature.type == 'gene':
                # With gene and exon features that are less than 15 nt long,
                # the annotation should be dropped from the output.
                if len([base for base in loc]) < 15:
                    raise
            feature.location = loc
        except Exception as e:
            raise Exception(e)
        return feature


class QualifierCheck:
    ''' This class contains functions to evaluate the quality of metadata.
    Args:
        lst_of_dcts (list): a list of dictionaries; example:
                            [{'foo': 'foobarqux', 'bar': 'foobarqux',
                              'qux': 'foobarqux'}, {'foo': 'foobarbaz',
                              'bar': 'foobarbaz', 'baz': 'foobarbaz'}]
        label (???): ?
    Returns:
        none
    Raises:
        Exception
    '''

    def __init__(self, lst_of_dcts, label):
        self.lst_of_dcts = lst_of_dcts
        self.label = label

    @staticmethod
    def _enforce_ASCII(lst_of_dcts):
        ''' This function converts any non-ASCII characters among
            qualifier values to ASCII characters. '''
        try:
            filtered_lst_of_dcts = [
                {k: unidecode(v) for k, v in list(dct.items())}
                for dct in lst_of_dcts]
        except:
            filtered_lst_of_dcts = [
                {k: unidecode(v.decode('utf-8')) for k, v in dct.items()}
                for dct in lst_of_dcts]
        return filtered_lst_of_dcts

    @staticmethod
    def _label_present(lst_of_dcts, label):
        ''' This function checks if each (!) list of dictionary keys
            of a list of dictionaries encompass the element <label> at
            least once. '''
        if not all(label in list(dct.keys()) for dct in lst_of_dcts):
            msg = 'ERROR: csv-file does not '\
                  'contain a column labelled %s' % (label)
            warnings.warn(msg)
            raise Exception
        return True

    @staticmethod
    def _rm_empty_qual(lst_of_dcts):
        ''' This function removes any qualifier from a dictionary which
            displays an empty value. Technically, this function
            loops through the qualifier dictionaries and removes any
            key-value-pair from a dictionary which contains an empty
            value. '''
        nonempty_lst_of_dcts = [{k: v for k, v in list(dct.items()) if v != ''}
                                for dct in lst_of_dcts]
        return nonempty_lst_of_dcts

    @staticmethod
    def _valid_INSDC_quals(lst_of_dcts):
        ''' This function checks if every (!) dictionary key in a list of
            dictionaries is a valid INSDC qualifier. '''
        keys_present = list(chain.from_iterable([list(dct.keys()) for dct in
                                                 lst_of_dcts]))
        not_valid = [k for k in keys_present if k not in
                     GlobVars.nex2ena_valid_INSDC_quals]
        if not_valid:
            msg = 'ERROR: The following are '\
                  'invalid INSDC qualifiers: %s' % (', '.join(not_valid))
            warnings.warn(msg)
            raise Exception
        return True

    def quality_of_qualifiers(self):
        ''' This function conducts a series of quality checks on the
            qualifiers list (a list of dictionaries). First (label_present),
            it checks if a qualifier matrix (and, hence, each entry)
            contains a column labelled with <seqname_col_label>.
            Second (nex2ena_valid_INSDC_quals), it checks if column
            names constitute valid INSDC feature table qualifiers.
        Args:
            label (str):  a string; example: 'isolate'
            lst_of_dcts (list): a list of dictionaries; example:
                                [{'isolate': 'taxon_A', 'country': 'Ecuador'},
                                 {'isolate': 'taxon_B', 'country': 'Peru'}]
        Returns:
            True, unless exception
        Raises:
            passed exception
        '''
        try:
            QualifierCheck._label_present(self.lst_of_dcts, self.label)
        except Exception as e:
            warnings.warn(e)
            raise Exception
        try:
            QualifierCheck._valid_INSDC_quals(self.lst_of_dcts)
        except Exception as e:
            warnings.warn(e)
            raise Exception
        return True
