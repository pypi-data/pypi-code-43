import os.path as path
import argparse
import re


def validate_multijaccard(ARGS):
    '''
    Validate command line arguments for multijaccard

    Parameters
    ----------
    ARGS : Namespace
        Command line arguments
    '''
    # check for files existing
    nonex_files = [b for b in ARGS.bed if not path.exists(b)]
    if len(nonex_files) != 0:
        raise OSError(' '.join([nonex_files[0], 'not found.']))
    # check there are the same number of names as BED files
    if ARGS.names is not None:
        names = ARGS.names.split(',')
        if len(names) != len(ARGS.bed):
            raise ValueError(
                '`names` and `beds` parameters must be the same length')
    else:
        names = None
    return {
        'beds': ARGS.bed,
        'names': names,
        'prefix': ARGS.prefix
    }


def validate_fastq_info(ARGS):
    '''
    Validate command line arguments for multijaccard

    Parameters
    ----------
    ARGS : Namespace
        Command line arguments
    '''
    # check file exists
    if not path.exists(ARGS.fastq):
        raise OSError('`{}` not found.'.format(ARGS.fastq))
    return {'fastq': ARGS.fastq}


def validate_filter_qname(ARGS):
    '''
    Validate command line arguments for filter-qname

    Parameters
    ----------
    ARGS : Namespace
        Command line arguments
    '''
    # check file exists
    if not path.exists(ARGS.fastq):
        raise OSError('`{}` not found.'.format(ARGS.fastq))
    return {'bam': ARGS.fastq}


def validate_organize(ARGS):
    '''
    Validate command line arguments for organize

    Parameters
    ----------
    ARGS : Namespace
        Command line arguments
    '''
    from data import DIRNAME_REGEX
    # check folder exists
    if not path.exists(ARGS.dir):
        raise OSError('`{}` not found.'.format(ARGS.dir))
    # check directory path matches expected regex for raw sequencing data
    # matches YYMMDD_InstrumentSerialNumber_RunNumber_(A|B)FlowcellID
    pattern = re.compile(DIRNAME_REGEX)
    if not pattern.fullmatch(ARGS.dir):
        raise OSError(
            '`{}` does not match the expected folder name format.'.format(
                ARGS.dir),
            'Should match `YYMMDD_InstrumentSerialNumber_RunNumber_(A|B)FlowcellID[_OPTIONAL_TEXT]`.'
        )
    return {'indir': ARGS.dir, 'outdir': ARGS.outdir, 'seqtype': ARGS.type}


def main():
    PARSER = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    SUBPARSERS = PARSER.add_subparsers(
        title='Sub-commands', dest='command', metavar='<command>')

    # multi-jaccard
    multijaccard_parser = SUBPARSERS.add_parser(
        'multi-jaccard',
        help='Perform `bedtools jaccard` on multiple BED files, and cluster samples by their pair-wise Jaccard indices.'
    )
    multijaccard_parser.add_argument(
        'bed',
        type=str,
        help="BED file(s)",
        nargs='+'
    )
    multijaccard_parser.add_argument(
        '-n', '--names',
        type=str,
        help="Comma-separated labels for BED files"
    )
    multijaccard_parser.add_argument(
        '-o', '--prefix',
        type=str,
        help='Prefix for output files.',
        default='jaccard'
    )

    # fastq-info
    fastqinfo_parser = SUBPARSERS.add_parser(
        'fastq-info',
        help='Extract metadata from read information in a FASTQ.'
    )
    fastqinfo_parser.add_argument(
        'fastq',
        type=str,
        help="BED file(s)"
    )

    # filter-qname
    filter_qname_parser = SUBPARSERS.add_parser(
        'filter-qname',
        help='Filter a SAM/BAM file by its query names'
    )
    filter_qname_parser.add_argument(
        'bam',
        type=str,
        help='Query name-sorted BAM file to be filtered'
    )
    filter_qname_parser.add_argument(
        'ids',
        type=str,
        help='Text file containing IDs to be removed'
    )
    filter_qname_parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file',
        default='filtered.bam'
    )

    # org
    org_parser = SUBPARSERS.add_parser(
        'org',
        help='Organize a batch of raw sequencing data'
    )
    org_parser.add_argument(
        'dir',
        type=str,
        help='Input directory to organize'
    )
    org_parser.add_argument(
        '-o', '--outdir',
        type=str,
        help='New path for input directory'
    )
    org_parser.add_argument(
        '-t', '--type',
        type=str,
        choices=['atac', 'dname', 'chip', 'dna', 'rna', 'hic', 'mix'],
        help='Type of sequencing data in batch.',
        default='mix'
    )

    # parse arguments from command line
    ARGS = PARSER.parse_args()

    # validate command line arguments for the give sub-command
    # import packages after parsing to speed up command line responsiveness
    if ARGS.command == 'multi-jaccard':
        validated_args = validate_multijaccard(ARGS)
        from .interval.multijaccard import multijaccard
        func = multijaccard
    elif ARGS.command == 'fastq-info':
        validated_args = validate_fastq_info(ARGS)
        from .fastx.fastq_info import fastq_info
        func = fastq_info
    elif ARGS.command == 'filter-qname':
        validated_args = validate_filter_qname(ARGS)
        from .align.filter_qname import filter_qname
        func = filter_qname
    elif ARGS.command == 'org':
        validated_args = validate_organize(ARGS)
        from .data.organize import organize
        func = organize
    else:
        pass
    # using the func = ... format allows for a single universal function call
    val = func(**validated_args)
    if val is not None:
        print(val)
