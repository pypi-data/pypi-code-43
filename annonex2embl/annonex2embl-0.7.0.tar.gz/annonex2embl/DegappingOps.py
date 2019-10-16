#!/usr/bin/env python
'''
Classes to degap sequences but maintain annotations
'''

#####################
# IMPORT OPERATIONS #
#####################

import warnings

from copy import copy
from itertools import count, groupby

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

class AddGapFeature:
    ''' This class contains a function that identifies a stretch of Ns
        in an input sequence and automatically adds a gap charset in
        its position.
    Args:
        seq (str):      a string that represents an aligned, degapped
                        DNA sequence; example: "ATGNNNC"
        charsets (dict):a dictionary with gene names (str) as keys and lists
                        of nucleotide positions (list) as values; example:
                        {"gene_1":[0,1],"gene_2":[2,3,4]}
    Returns:
        tupl.   The return consists of the input sequence and the
                corresponding charsets (plus a gap charset, if
                appropriate); example: (degapped_seq, degapped_charsets)
    Raises:
        currently nothing
    '''

    def __init__(self, seq, charsets):
        self.seq = seq
        self.charsets = charsets

    def add(self):
        ''' This function was developed while reviewing the following answer on SO:
            https://stackoverflow.com/questions/25211905/determine-length-of-polypurine-tract '''
        seq = self.seq
        charsets = self.charsets
        annotations = copy(charsets)
        gap_indices = [i for i, nucl in enumerate(seq) if nucl=="N"]  # Indexing all 'N' in seq
        gap_ranges = [list(g) for _,g in groupby(gap_indices, key=lambda n, c=count(): n-next(c))]
        if gap_ranges:
            for countr, rnge in enumerate(gap_ranges):
                try:
                    annotations["gap"+str(countr)] = rnge
                except Exception as e:
                    warnings.warn("Cannot process Ns in positions %s." % (','.join(rnge)))
        return seq, annotations

class DegapButMaintainAnno:
    ''' This class contains a function to degap DNA sequences while
        maintaining annotations. Specifically, the functions remove
        dashes from strings while maintaining annotations on these
        strings. Only some of the implementations work if the charsets
        are overlapping.
    Args:
        seq (str):      a string that represents an aligned DNA sequence;
                        example: "ATG-C"
        charsets (dict):a dictionary with gene names (str) as keys and lists
                        of nucleotide positions (list) as values; example:
                        {"gene_1":[0,1],"gene_2":[2,3,4]}
    Returns:
        tupl.   The return consists of the degapped sequence and the
                corresponding degapped charsets; example:
                (degapped_seq, degapped_charsets)
    Raises:
        currently nothing
    '''

    def __init__(self, seq, rmchar, charsets):
        self.seq = seq
        self.rmchar = rmchar
        self.charsets = charsets

    def degap(self):
        ''' This function works on overlapping charsets and is preferable over
        "degap_legacy".
        Source: http://stackoverflow.com/questions/35233714/
        maintaining-overlapping-annotations-while-removing-dashes-from-string
        '''

        seq = self.seq
        rmchar = self.rmchar
        charsets = self.charsets
        annotations = copy(charsets)
        index = seq.find(rmchar)
        while index > -1:  # if any occurrence is found
            for gene_name, indices in list(annotations.items()):
                if index in indices:
                    indices.remove(index)
                annotations[gene_name] = [e-1 if e > index else e
                                          for e in indices]
            seq = seq[:index] + seq[index+1:]
            index = seq.find(rmchar)
        return seq, annotations


class RmAmbigsButMaintainAnno:
    ''' This class removes ambiguous nucleotides from a DNA sequence
        while maintaining the annotations.
    Args:
        seq (str):      a string that represents an aligned DNA sequence;
                        example: "NNATGCNNN"
        charsets (dict):a dictionary with gene names (str) as keys and lists
                        of nucleotide positions (list) as values; example:
                        {"gene_1":[0,1,2,3],"gene_2":[4,5,6,7,8]}
    Returns:
        tupl.   The return consists of the shortened DNA sequence and
                the corresponding shortened charsets; example:
                (shortened_seq, shortened_charsets)
    Raises:
        currently nothing
    '''

    def __init__(self):
        pass

    @staticmethod
    def rm_leadambig(seq, rmchar, charsets):
        ''' This class removes leading ambiguous nucleotides from a DNA
            sequence while maintaining the annotations. '''
        if seq[0] == rmchar:
            lead_stripoff = len(seq)-len(seq.lstrip(rmchar))
            for gene_name, indices in list(charsets.items()):
                indices_shifted = [i-lead_stripoff for i in indices]
                charsets[gene_name] = [i for i in indices_shifted if i >= 0]
            seq = seq[lead_stripoff:]
        return seq, charsets

    @staticmethod
    def rm_trailambig(seq, rmchar, charsets):
        ''' This class removes trailing ambiguous nucleotides from a DNA
            sequence while maintaining the annotations. '''
        if seq[-1] == rmchar:
            trail_stripoff = len(seq.rstrip(rmchar))
            range_stripoff = list(range(trail_stripoff, len(seq)))
            for gene_name, indices in list(charsets.items()):
                indices_new = copy(indices)
                for index in range_stripoff:
                    if index in indices_new:
                        indices_new.remove(index)
                #    else:
                #        warnings.warn("Index %s out of range." %(index))
                charsets[gene_name] = indices_new
            seq = seq[:trail_stripoff]
        return seq, charsets
