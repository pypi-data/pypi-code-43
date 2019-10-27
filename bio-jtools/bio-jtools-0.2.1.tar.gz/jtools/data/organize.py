from __future__ import division, absolute_import, print_function
import re
from datetime import datetime
from os import listdir, mkdir, rename
import os.path as path
from . import DIRNAME_REGEX, FASTQ_FILENAME_REGEX, RESERVED_DIRS, RESERVED_FILENAMES, README_STR, CLUSTER_STR, SETUP_STR, SNAKEFILE_STR


def fetch_seq_info(dirname):
    '''
    Extract sequencing batch information from input directory filename

    Parameters
    ----------
    dirname : str
        Directory filename to parse
    '''
    # check directory path matches expected regex for raw sequencing data
    # matches YYMMDD_InstrumentSerialNumber_RunNumber_(A|B)FlowcellID[_OPTIONAL_TEXT]
    # see https://www.biostars.org/p/124972/, https://www.biostars.org/p/198143/
    pattern = re.compile(DIRNAME_REGEX)
    m = re.match(pattern, dirname)
    vals = {
        'date': datetime.strptime(''.join([m.group(1), m.group(2), m.group(3)]), '%y%m%d'),
        'instrument': m.group(4),
        'run': m.group(5),
        'position': m.group(6),
        'flowcell': m.group(7),
        'date_sub': '',
        'description': m.group(8)
    }
    vals['date_rec'] = vals['date'].strftime('%Y-%m-%d')
    return vals


def create_cluster_params(outfile):
    '''
    Create `cluster.yaml` file

    Parameters
    ----------
    outfile : str
        Output config file to create
    '''
    fh = open(outfile, 'w')
    fh.write(CLUSTER_STR)
    fh.close()


def create_readme(seq_info, outfile):
    '''
    Create `README.md` file

    Parameters
    ----------
    seq_info : Dict of {str, Object}
        Sequencing metadata retrieved from directory name
    outfile : str
        Output config file to create
    '''
    fh = open(outfile, 'w')
    fh.write(README_STR.format(**seq_info))
    fh.close()


def create_config(fastq_dir, outfile):
    '''
    Create `config.tsv` file

    Parameters
    ----------
    fastq_dir : str
        Directory containing FASTQs files to parse
    outfile : str
        Output config file to create
    '''
    import pandas as pd
    # record renaming actions
    actions = []
    # get all FASTQs in directory
    fastqs = listdir(fastq_dir)
    # create placholder for tracking samples and their respective files
    samples_dict = {}
    # check that file names match FASTQ regex
    pattern = re.compile(FASTQ_FILENAME_REGEX)
    for f in fastqs:
        # extract sample information from file name
        m = pattern.match(f)
        if m is None:
            continue
        name = m.group(1)
        index = m.group(2)
        lane = m.group(3)
        mate = m.group(4)
        zipped = m.group(5)
        cname = correct_sample_name(name)
        if cname not in samples_dict:
            samples_dict[cname] = {'sid': index, 'lanes': set([lane]), 'mates': set([mate])}
        else:
            if index != samples_dict[cname]['sid']:
                raise IOError('`{}` has multiple indexes on this same flowcell: {}'.format(
                    f, ' '.join(index, samples_dict[cname]['sid'])))
            else:
                samples_dict[cname]['lanes'].add(lane)
                samples_dict[cname]['mates'].add(mate)
        # create new file name for FASTQ
        # remove sample indexes and `_001` from file names
        newf = '_'.join([cname, 'L00' + lane, mate]) + '.fastq' + zipped
        src = path.join(fastq_dir, f)
        dest = path.join(fastq_dir, newf)
        # rename files if they don't abide by the format
        if src != dest:
            rename(src, dest)
            actions.append(' '.join([src, '->', dest]))
    # fill in sample configuration table for config.tsv
    samples_df = pd.DataFrame(columns=['Sample', 'Sample_Index_Number', 'Lanes', 'Mates'])
    for k, v in samples_dict.items():
        samples_df = samples_df.append(
            {
                'Sample': k,
                'Sample_Index_Number': v['sid'],
                'Lanes': ','.join(v['lanes']),
                'Mates': ','.join(v['mates'])
            },
            ignore_index=True
        )
    # write table to outfile
    samples_df.to_csv(outfile, sep='\t', index=False)
    return actions


def correct_sample_name(name):
    '''
    Correct FASTQ's sample name to match the following regex: '[A-Za-z0-9-]+'.

    Parameters
    ----------
    name : str
        Filename to be corrected
    '''
    newname = name.replace('_', '-')
    return newname


def create_snakefile(seqtype, outfile):
    '''
    Create `Snakefile` config file

    Parameters
    ----------
    seqtype : str
        Type of sequencing data contained in the input folder.
        Must be one of ['atac', 'dname', 'chip', 'dna', 'rna', 'hic', 'mix'].
    outfile : str
        Output config file to create
    '''
    # write to Snakefile
    fh = open(outfile, 'w')
    fh.write(SNAKEFILE_STR)
    fh.close()


def organize(indir, outdir=None, seqtype='mix'):
    '''
    Organize raw sequencing data folder

    Parameters
    ----------
    indir : str
        Input directory to organize
    outdir : str
        New path for input directory
    seqtype : str
        Type of sequencing data contained in the input folder.
        Must be one of ['atac', 'dname', 'chip', 'dna', 'rna', 'hic', 'mix'].
    '''
    # record steps performed during setup
    setup_log = {'mkdir': [], 'mv': [], 'res_files': [], 'fastq': []}
    # extract sequencing metadata information from directory name
    seq_info = fetch_seq_info(indir)
    default_dirs = RESERVED_DIRS
    if seqtype == 'atac' or seqtype == 'chip':
        default_dirs += ['Peaks']
    elif seqtype == 'dname':
        default_dirs += ['Methylation']
    elif seqtype == 'hic':
        default_dirs += ['Contacts']
    # make directories
    for d in default_dirs:
        dir_to_make = path.join(indir, d)
        if not path.exists(dir_to_make):
            mkdir(dir_to_make)
            # add action to setup log
            setup_log['mkdir'].append(d)
    # find FASTQs in directory
    dir_files = listdir(indir)
    fastq_files = [f for f in dir_files if f.endswith('.fastq.gz')]
    other_files = [f for f in dir_files if not f.endswith('.fastq.gz') and f not in RESERVED_FILENAMES]
    # move FASTQs into `FASTQs` directory
    for f in fastq_files:
        src = path.join(indir, f)
        dest = path.join(indir, 'FASTQs', f)
        rename(src, dest)
        # add action to setup log
        setup_log['mv'].append(' '.join([src, '->', dest]))
    for f in other_files:
        src = path.join(indir, f)
        dest = path.join(indir, 'Reports', f)
        if not path.isdir(src):
            rename(src, dest)
            # add action to setup log
            setup_log['mv'].append(' '.join([src, '->', dest]))
        else:
            if f not in RESERVED_DIRS:
                rename(src, dest)
                # add action to setup log
                setup_log['mv'].append(' '.join([src, '->', dest]))
    # check for README and other config files in directory
    reserved_files = [path.join(indir, f) for f in RESERVED_FILENAMES]
    if not path.exists(reserved_files[0]):
        create_readme(seq_info, reserved_files[0])
        # add action to setup log
        setup_log['res_files'].append(reserved_files[0])
    if not path.exists(reserved_files[1]):
        create_cluster_params(reserved_files[1])
        # add action to setup log
        setup_log['res_files'].append(reserved_files[1])
    # create config and add all renaming events to setup log
    setup_log['fastq'] = create_config(path.join(indir, RESERVED_DIRS[1]), reserved_files[2])
    # add creation of config file to setup log
    setup_log['res_files'].append(reserved_files[2])
    if not path.exists(reserved_files[3]):
        create_snakefile(seqtype, reserved_files[3])
        # add action to setup log
        setup_log['res_files'].append(reserved_files[3])
    # reformat setup_log for printing
    setup_log_printable = {}
    for k, v in setup_log.items():
        if len(v) > 0:
            setup_log_printable[k] = '\n'.join(setup_log[k])
        else:
            setup_log_printable[k] = ''
    fh = open(path.join(indir, 'setup.log'), 'w')
    fh.write(SETUP_STR.format(**setup_log_printable))
    fh.close()
    # rename directory if asked to
    if outdir is not None:
        rename(indir, outdir)
