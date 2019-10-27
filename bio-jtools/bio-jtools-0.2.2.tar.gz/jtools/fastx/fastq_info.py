from Bio import SeqIO
from gzip import open as gzopen
from itertools import islice, zip_longest
import sys

def grouper(iterable, n, fillvalue=None):
    '''
    Collect data into fixed-length chunks or blocks

    Parameters
    ----------
    iterable : 
        Path to FASTQ file
    '''
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def parse_read_id(read_id, tag=None):
    '''
    Extract metadata from a read ID

    Parameters
    ----------
    read_id : str
        Read ID
    tag : str
        Tag to extract from metadata
    '''
    split_info = read_id.split(':')
    tags = ['instrument', 'run', 'flowcell', 'lane', 'tile', 'x', 'y']
    meta = dict(zip(tags, split_info))
    if tag is not None and tag in tags:
        return meta[tag]
    else:
        return meta
    

def fastq_info(fastq, chunksize=10000):
    '''
    Extract flowcell and other metadata from a FASTQ

    Parameters
    ----------
    fastq : str
        Path to FASTQ file
    chunksize : int
        Number of records to read simultaneously
    '''
    # check for file format
    if fastq.endswith('.gz'):
        fq_handle = gzopen(fastq, 'rt')
    else:
        fq_handle = open(fastq, 'r')
    # load reads for random access
    records = SeqIO.parse(fq_handle, 'fastq')
    # data structure for managing metadata
    metadata = {
        'flowcells': set([]),
        'n_reads': 0
    }
    # load `chunksize` reads at a time
    chunked_records = grouper(records, chunksize)
    for chunk in chunked_records:
        # filter chunk
        chunk = [r for r in chunk if r is not None]
        # count reads
        metadata['n_reads'] += len(chunk)
        # extract unique flowcell IDs
        flowcells = set([parse_read_id(r.id, 'flowcell') for r in chunk])
        for f in flowcells:
            metadata['flowcells'].add(f)

    fq_handle.close()
    return metadata

