#!/usr/bin/env python2.7

''' Main operations in annonex2embl '''

#####################
# IMPORT OPERATIONS #
#####################

import CheckingOps as CkOps
import DegappingOps as DgOps
import GenerationOps as GnOps
import GlobalVariables as GlobVars
import ParsingOps as PrOps
import IOOps as IOOps
import sys
import os
import gzip
import warnings

from Bio import SeqIO
#from Bio.Alphabet import generic_dna
#from Bio.Seq import Seq
from Bio import SeqFeature
from collections import OrderedDict
from copy import copy
from copy import deepcopy
from distutils.util import strtobool
from unidecode import unidecode

# Add specific directory to sys.path in order to import its modules
# Note: This relative importing is amateurish. Could the following
#       import be replaced with 'import annonex2embl'?
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'annonex2embl'))

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

# To format warnings in a pretty, readable way:
def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return '\n annonex2embl %s\n' % (message)
warnings.formatwarning = warning_on_one_line

###########
# CLASSES #
###########

#############
# FUNCTIONS #
#############


warnings.formatwarning = warning_on_one_line

def annonex2embl(path_to_nex,
                 path_to_csv,
                 descr_DEline,
                 email_addr,
                 author_names,
                 path_to_outfile,

                 manifest_study='',
                 manifest_descr='',
                 product_lookup='False',
                 tax_check='False',
                 linemask='False',
                 topology='linear',
                 tax_division='PLN',
                 uniq_seqid_col='isolate',
                 transl_table='11',
                 organelle='plastid',
                 seq_version='1',
                 compress='False'):

########################################################################

# 0. MAKE SPECIFIC VARIABLES BOOLEAN
    productlookup_bool = strtobool(product_lookup)
    taxcheck_bool = strtobool(tax_check)
    linemask_bool = strtobool(linemask)
    compress_bool = strtobool(compress)

########################################################################

# 1. OPEN OUTFILE
    with open(path_to_outfile, 'a') as outp_handle:

########################################################################

# 2. PARSE DATA FROM .NEX-FILE
        try:
            charsets_global, alignm_global = IOOps.Inp().\
                parse_nexus_file(path_to_nex)
        except Exception as e:
            msg = 'ERROR: %s' % (e)
            warnings.warn(msg)
            raise Exception

########################################################################

# 3. PARSE DATA FROM .CSV-FILE
        try:
            raw_qualifiers = IOOps.Inp().parse_csv_file(path_to_csv)
        except Exception as e:
            msg = 'ERROR: %s' % (e)
            warnings.warn(msg)
            raise Exception

########################################################################

# 4.1 CHECK QUALIFIERS
# 4.1.1 Perform quality checks on qualifiers
        try:
            CkOps.QualifierCheck(raw_qualifiers, uniq_seqid_col).\
                quality_of_qualifiers()
        except Exception as e:
            msg = 'ERROR: %s' % (e)
            warnings.warn(msg)
            raise Exception
    # 4.1.2 Remove qualifiers without content (i.e. empty qualifiers)
        nonempty_qualifiers = CkOps.QualifierCheck.\
            _rm_empty_qual(raw_qualifiers)
    # 4.1.3 Enforce that all qualifier values consist of ASCII characters
        filtered_qualifiers = CkOps.QualifierCheck.\
            _enforce_ASCII(nonempty_qualifiers)

####################################

# 4.2 CHECK SEQUENCES
        sorted_seqnames = sorted(alignm_global.keys())
        sorted_seqids = sorted([d[uniq_seqid_col] for d in filtered_qualifiers])
    # 4.2.1. Exit if seq names in NEX-file not identical to seq ids in csv-file
        try:
            not_shared = list(set(sorted_seqnames) - set(sorted_seqids))
        except Exception as e:
            msg = 'ERROR: Sequence names in %s are NOT IDENTICAL to sequence IDs in %s.'\
                  '%s The following sequence names don\'t have a match: %s'\
                  % (path_to_nex, path_to_csv, '\n', ','.join(not_shared))
            warnings.warn(msg)
            raise Exception

########################################################################

# 5. PARSE OUT FEATURE KEY, OBTAIN OFFICIAL GENE NAME AND GENE PRODUCT
        charset_dict = {}
        for charset_name in list(charsets_global.keys()):
            try:
                charset_sym, charset_type, charset_orient, charset_product = PrOps.\
                    ParseCharsetName(charset_name, email_addr, productlookup_bool).parse()
            except Exception as e:
                msg = 'ERROR: %s' % (e)
                warnings.warn(msg)
                raise Exception
            charset_dict[charset_name] = (charset_sym, charset_type, charset_orient,
                                          charset_product)

########################################################################

# 6. GENERATING SEQ_RECORDS BY LOOPING THROUGH EACH SEQUENCE OF THE ALIGNMENT
#    Work off the sequences alphabetically.
        for counter, seq_name in enumerate(sorted_seqnames):
            # TFLs generate safe copies of charset and alignment for every loop iteration; however, the cmd "copy()" itself would not work because it cannot operate on lists of lists; thus, we use "deepcopy()", which can.
            charsets_withgaps = deepcopy(charsets_global)
            alignm = deepcopy(alignm_global)

####################################

# 6.1. SELECT CURRENT SEQUENCES AND CURRENT QUALIFIERS
            current_seq = alignm[seq_name]
            current_quals = [d for d in filtered_qualifiers
                             if d[uniq_seqid_col] == seq_name][0]

####################################

# 6.2. GENERATE THE BASIC SEQ_RECORD (I.E., WITHOUT FEATURES)

# 6.2.1. Generate the basic SeqRecord
            seq_record = GnOps.GenerateSeqRecord().base_record(
                current_seq, current_quals, uniq_seqid_col, seq_version,
                descr_DEline, topology, tax_division, organelle)
            # Add a function that automatically removes all sequences
            # that consist only of Ns (or ?s).
            skip = True
            for i in seq_record.seq:
                if i != 'N' and i != '?':
                    skip = False
                    break
            if skip:
                continue

####################################

# 6.3. CLEAN UP THE SEQUENCE OF THE SEQ_RECORD (i.e., remove leading or
#      trailing ambiguities, remove gaps), but maintain correct
#      annotations.
#      Note 1: This clean-up has to occur before (!) the SeqFeature
#      'source' is generated, as the source feature provides info on
#      the full sequence length.
#      Note 2: Charsets are identical across all sequences.

# 6.3.1. Replace question marks in DNA sequence with 'N'
            seq_record.seq._data = seq_record.seq._data.replace('?', 'N')
            # TFL generates a safe copy of sequence to work on
            seq_withgaps = copy(seq_record.seq)

# 6.3.2. Skip all sequence records smaller than 10 unambiguous nucleotides
            if len(seq_record.seq._data.replace('-','').strip('N')) <= 10:
                msg = 'WARNING: Sequence `%s` not saved because shorter than 10 '\
                      'unambiguous nucleotides.' % (seq_record.id)
                warnings.warn(msg)
                continue

# 6.3.3. Remove leading ambiguities while maintaining correct annotations
            seq_noleadambigs, charsets_noleadambigs = DgOps.\
                RmAmbigsButMaintainAnno().rm_leadambig(seq_withgaps, 'N',
                                                       charsets_withgaps)

# 6.3.4. Remove trailing ambiguities while maintaining correct annotations
            seq_notrailambigs, charsets_notrailambigs = DgOps.\
                RmAmbigsButMaintainAnno().rm_trailambig(seq_noleadambigs,
                                                        'N', charsets_noleadambigs)
# 6.3.5. Degap the sequence while maintaining correct annotations
            seq_nogaps, charsets_degapped = DgOps.\
                DegapButMaintainAnno(seq_notrailambigs, '-',
                                     charsets_notrailambigs).degap()

# 6.3.6. Add gap features where stretches of Ns in sequence
            seq_final, charsets_final = DgOps.\
                AddGapFeature(seq_nogaps, charsets_degapped).add()
            # TFL assigns the deambiged and degapped sequence back
            seq_record.seq = seq_final

####################################

# 6.4. GENERATE SEQFEATURE 'SOURCE' AND TEST TAXON NAME AGAINST
#      NCBI TAXONOMY

# 6.4.1. Generate SeqFeature 'source' and append to features list
            charset_names = list(charsets_final.keys())
            source_feature = GnOps.GenerateSeqFeature().\
                source_feat(len(seq_record), current_quals, charset_names)
            seq_record.features.append(source_feature)

####################################

# 6.5. VALIDATE TAXON NAME

# 6.5.1. Test taxon name against NCBI taxonomy; if not listed, adjust
#        taxon name and append ecotype info
            if taxcheck_bool:
                seq_record = PrOps.ConfirmAdjustTaxonName().go(seq_record,
                                                               email_addr)

####################################

# 6.6. POPULATE THE FEATURE KEYS WITH THE CHARSET INFORMATION
#      Note: Each charset represents a dictionary that must be added in
#      full to the list "SeqRecord.features"

            for charset_name, charset_range in list(charsets_final.items()):

# 6.6.1. Proceed in loop only if charset_range is not empty
#        An empty charset_range could be the case if the charset only
#        consisted of 'N' (which were removed in steps 6.3.2 and 6.3.3).
                if charset_range:
# 6.6.2. Convert charset_range into Location Object
                    location_object = GnOps.GenerateFeatLoc().make_location(charset_range)

# 6.6.3. Assign a gene product to a gene name, unless it's a gap feature
                    if charset_name[0:3] == "gap":
                        charset_sym = None
                        charset_type = "gap"
                        charset_orient = "forw"
                        charset_product = None
                    else:
                        charset_sym, charset_type, charset_orient, charset_product = charset_dict[charset_name]

# 6.6.4. Generate a regular SeqFeature and append to seq_record.features
#        Note: The position indices for the stop codon are truncated in
#              this step.
                    seq = []
                    [seq.append(seq_record[obj]) for obj in location_object]
                    seq = ''.join(seq)

                    seq_feature = GnOps.GenerateSeqFeature().regular_feat(
                        charset_sym, charset_type, charset_orient, location_object, transl_table,
                        seq, charset_product)
                    seq_record.features.append(seq_feature)

####################################

# 6.7. SORT ALL SEQ_RECORD.FEATURES EXCEPT THE FIRST ONE (WHICH
#      CONSTITUTES THE SOURCE FEATURE) BY THEIR RELATIVE START
#      POSITIONS
            sorted_features = sorted(seq_record.features[1:],
                                     key=lambda x: x.location.start.position)
            seq_record.features = [seq_record.features[0]] + sorted_features

####################################

# 6.8. TRANSLATE AND CHECK QUALITY OF TRANSLATION
            removal_list = []
            last_seen = ["type", "before", "after"]
            for indx, feature in enumerate(seq_record.features):
                # Check if feature is a coding region
                if feature.type == 'CDS' or feature.type == 'gene':
                    try:
                        # In TFL, features are truncated to the first
                        # internal stop codon, if present.
                        last_seen[0] = feature.type
                        last_seen[1] = feature.location
                        feature = CkOps.TranslCheck().\
                            transl_and_quality_of_transl(seq_record,
                                                         feature, transl_table)
                        last_seen[2] = feature.location
                    except Exception as e:
                        msg = 'WARNING: Feature `%s` (type: %s) of sequence `%s` is not saved to '\
                              'output. Reason: %s' % (feature.id, feature.type, seq_record.id, e)
                        warnings.warn(msg)
                        removal_list.append(indx)
                elif feature.type == 'IGS' or feature.type == 'intron':
                    if  last_seen[0] == 'CDS' or last_seen[0] == 'gene':
                        if not last_seen[1] == last_seen[2]:
                            feature.location = CkOps.TranslCheck().\
                                                    adjustLocation(feature.location, last_seen[2])
                    last_seen = ["type","loc_before","loc_after"]
                else:
                    last_seen = ["type","loc_before","loc_after"]
            # TFL removes the objects in reverse order, because otherwise
            # each removal would shift the indices of subsequent objects
            # to the left.
            for indx in sorted(removal_list, reverse=True):
                seq_record.features.pop(indx)

####################################

# 6.9. INTRODUCE FUZZY ENDS
            for feature in seq_record.features:
                # Check if feature is a coding region
                if feature.type == 'CDS' or feature.type == 'gene':
                    # Note: Don't use "feature.extract(seq_record.seq)" in TFLs,
                    #       as stop codon was truncated from feature under
                    #       Step 6.8, because in an ENA record, the AA sequence
                    #       of the translation does not have the stop codon
                    #       (i.e., the '*'), while the feature location
                    #       range (i.e., 738..2291) very much includes
                    #       its position (which is biologically logical).
                    charset_range_updated = list(range(feature.location.start.position,
                        feature.location.end.position))
                    coding_seq = ''.join([seq_record.seq[i] for i in charset_range_updated])
                    if feature.location._get_strand() == -1:
                        coding_seq = PrOps.SequenceParsing.reverseComplement(coding_seq)
                        feature.location.parts = feature.location.parts[::-1] # if feature reverse, the feature components list must be inverted
                    if not coding_seq.startswith(GlobVars.nex2ena_start_codon):
                        feature.location = GnOps.GenerateFeatLoc().\
                            make_start_fuzzy(feature.location)
                    if all([not coding_seq.endswith(c)
                            for c in GlobVars.nex2ena_stop_codons]):
                                feature.location = GnOps.GenerateFeatLoc().\
                                make_end_fuzzy(feature.location)


# (FUTURE)  Also introduce fuzzy ends to features when those had leading or trailing Ns removed,
#           because the removed Ns may constitute start of stop codons.

####################################

# 6.10. DECISION ON OUTPUT FORMAT
            IOOps.Outp().write_SeqRecord(seq_name, seq_record,
                                         author_names, outp_handle,
                                         linemask_bool)

########################################################################

# 7. CREATE COMPRESSED FILE

    if compress_bool:
        with open(path_to_outfile, 'r') as outp_handle:
            lines = outp_handle.readlines()
        with gzip.open(path_to_outfile + '.gz', 'wb') as outp_handle:
            for line in lines:
                try:
                    outp_handle.write(bytearray(line, 'utf-8'))
                except Exception as e:
                    try:
                        outp_handle.write(line)
                    except Exception as e:
                        msg = 'WARNING: EMBL flatfile not compressed '\
                              'due to error: %s' % (e)
                        warnings.warn(msg)

########################################################################

# 8. CREATE MANIFEST FILE

    if manifest_study and manifest_descr:
        manifest_flatfile = os.path.basename(path_to_outfile)
        if compress_bool:
            IOOps.Outp().create_manifest(path_to_outfile,
                                        manifest_study,
                                        manifest_descr,
                                        manifest_flatfile+'.gz')
        else:
            IOOps.Outp().create_manifest(path_to_outfile,
                                        manifest_study,
                                        manifest_descr,
                                        manifest_flatfile)

    elif manifest_study and not manifest_descr:
        msg = 'WARNING: Manifest file not written '\
              'due to missing manifest name.'
        warnings.warn(msg)

    elif not manifest_study and manifest_descr:
        msg = 'WARNING: Manifest file not written '\
              'due to missing manifest study.'
        warnings.warn(msg)
    else:
        pass

########################################################################
