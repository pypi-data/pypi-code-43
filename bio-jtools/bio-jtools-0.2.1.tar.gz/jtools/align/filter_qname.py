from __future__ import division, absolute_import, print_function
import pysam
from tqdm import tqdm
from ..utils import detect_filetype_from_path


def samprint(alignment, output=None):
    '''
    Print to output file or STDOUT if none is supplied

    Parameters
    ----------
    alignment : pysam.AlignedSegment
        Alignment to be written
    outfile : str
        Output file
    '''
    if output is None:
        print(alignment)
    else:
        output.write(alignment)


def filter_qname(bamfile, idfile, outfile=None):
    '''
    Filter reads in a SAM/BAM file by their query names
    '''
    # read in name-sorted BAM file
    bam = pysam.AlignmentFile(bamfile, "rb")
    # output BAM file
    ftype = detect_filetype_from_path(outfile)
    if ftype is None:
        output = None
    elif ftype == 'SAM':
        output = pysam.AlignmentFile(outfile, "w", template=bam)
    elif ftype == 'BAM':
        output = pysam.AlignmentFile(outfile, "wb", template=bam)
    else:
        raise ValueError("Unknown output file format for `outfile`: {}".format(outfile))
    #  read in IDs to be removed (list(set(...)) to only keep unique IDs)
    ids = list(set([l.rstrip() for l in open(idfile, 'r').readlines()]))
    # sort IDs to match BAM for efficient processing (destructive function)
    ids.sort(key=str.lower, reverse=True)
    n_ids = len(ids)
    # progress bar using total alignment counts
    pbar = tqdm()
    reads = bam.fetch(until_eof=True)
    read = next(reads)
    # variable for ensuring BAM is sorted by query name
    last_q = reads.query_name
    while True:
        if read.query_name < last_q:
            raise ValueError(
                'Alignment file is not sorted. {} < {}'.format(read.query_name, last_q)
            )
        # if read name is greater than current top of stack
        if read.query_name > ids[-1]:
            # if this is the last ID
            if n_ids == 1:
                # write remaining reads to new file and break out of while loop
                samprint(read, output)
                for r in bam:
                    samprint(read, output)
                break
            # otherwise pop that ID, try again
            else:
                ids.pop()
                n_ids -= 1
        # skip reads that match the top of the stack
        elif read.query_name == ids[-1]:
            read = next(reads)
        # if read name is less that top of stack, write it and move on
        else:
            samprint(read, output)
            last_q = read.query_name
            read = next(reads)
        pbar.update()
    if output is not None:
        output.close()
