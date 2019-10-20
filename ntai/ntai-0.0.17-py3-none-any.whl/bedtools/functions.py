import os, sys, uuid
from ..terminal.tools import arg

def complement(
    i:str,
    g:str,
    L:bool=False,
    s:bool=False,
):
    '''
    Arguments:
        i (str): input file.
        g (str): the genome file.
        L (bool): Limit the output to solely the chromosomes that are
            represented in the -i file. Chromosomes that are in -g but not -i
            will be suppressed.
        s (bool): Force strandedness. That is, only merge features that are the
            same strand. By default, this is disabled.


    '''
    arg_i = arg('i', i)
    arg_g = arg('g', g)
    arg_L = arg('L', L, flag=True)
    arg_s = arg('s', s, flag=True)

    command = [
        'bedtools',
        'complement',
        *arg_i, *arg_g, *arg_L, *arg_s,
    ]
    return command

def merge(
    i:str,
    s:bool=False,
    S:str=None,
    d:int=0,
    c:str=None,
    o:str=None,
    header:bool=False,
    delim:str=';'
):
    '''
    Arguments:
        i (str): input file.

        s (bool): Force strandedness. That is, only merge features that are the
            same strand. By default, this is disabled.

        S (str): Force merge for one specific strand only. Follow with + or - to
            force merge from only the forward or reverse strand, respectively.
            By default, merging is done without respect to strand.

        d (int): Maximum distance between features allowed for features to be
            merged. Default is 0. That is, overlapping and/or book-ended
            features are merged.

        c (str): specify columns from the input file to operate upon
            (see -o option, below). Multiple columns can be specified in a
            comma-delimited list.

        o (str): Specify the operation that should be applied to -c.
            Valid operations:
                sum, min, max, absmin, absmax, mean, median,
                collapse (i.e., print a delimited list (duplicates allowed)),
                distinct (i.e., print a delimited list (NO duplicates allowed)),
                count
                count_distinct (i.e., a count of the unique values in the column),
            Default: sum
                Multiple operations can be specified in a comma-delimited list.
                If there is only column, but multiple operations, all operations
                will be applied on that column. Likewise, if there is only one
                operation, but multiple columns, that operation will be applied
                to all columns. Otherwise, the number of columns must match the
                number of operations, and will be applied in respective order.

                E.g., -c 5,4,6 -o sum,mean,count will give the sum of column 5,
                the mean of column 4, and the count of column 6.
                The order of output columns will match the ordering given in the
                command.

        header (bool): Print the header from the A file prior to results.

        delim (str): Specify a custom delimiter for the -nms and -scores concat
            options
                Example: -delim "|"
                Default: ";"

    Returns:
        command (list): a list of strings containing the bedtools getfasta
            command
    '''
    arg_i = arg('i', i)
    arg_s = arg('s', s, flag=True)
    arg_S = arg('S', S)
    arg_d = arg('d', d)
    arg_c = arg('c', c)
    arg_o = arg('o', o)
    arg_header = arg('header', header, flag=True)
    arg_delim  = arg('delim', delim)

    command = [
        'bedtools',
        'merge',
        *arg_i, *arg_s, *arg_S,
        *arg_d, *arg_c, *arg_o,
        *arg_header, *arg_delim
    ]
    return command



def getfasta(
    fi:     str,
    bed:    str = '/dev/stdin',
    fo:     str = '/dev/stdout',
    name:   bool = False,
    tab:    bool = False,
    bedOut: bool = False,
    s:      bool = False,
    split:  bool = False
) -> list:
    '''
    Arguments:
        fi (str): input FASTA

        bed (str): <BED/GFF/VCF>

        fo (str): Specify an output file name. By default, output goes to stdout

        name (bool): Use the “name” column in the BED file for the FASTA headers
            in the output FASTA file.

        tab (bool): Report extract sequences in a tab-delimited format instead
            of in FASTA format.

        bedOut (bool): Report extract sequences in a tab-delimited BED format
            instead of in FASTA format.

        s (bool): Force strandedness. If the feature occupies the antisense
            strand, the sequence will be reverse complemented. Default: strand
            information is ignored.

        split (bool): Given BED12 input, extract and concatenate the sequences
            from the BED “blocks” (e.g., exons)
    Returns:
        command (list): a list of strings containing the bedtools getfasta
            command
    '''
    arg_fi = arg('fi', fi)
    arg_bed = arg('bed', bed)
    arg_fo = arg('fo', fo)
    arg_name = arg('name', name, flag=True)
    arg_tab = arg('tab', tab, flag=True)
    arg_bedOut = arg('bedOut', bedOut, flag=True)
    arg_s = arg('s', s, flag=True)
    arg_split = arg('split', split, flag=True)
    command = [
        'bedtools',
        'getfasta',
        *arg_fi, *arg_bed, *arg_fo, *arg_name,
        *arg_tab, *arg_bedOut, *arg_s, *arg_split,
    ]
    return command
