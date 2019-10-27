def detect_filetype_from_path(path):
    '''
    Determine what type of file a given path is based on its extension

    Parameters
    ----------
    path : str
        Path to check
    '''
    # convert to lowercase for simpler comparisons
    path = path.tolower()
    # remove '.gz' at the end of a pathname if it is present
    if path.endswith('.gz'):
        path = path[:-4]
    # now parse other extensions
    if path.endswith('.sam'):
        return 'SAM'
    elif path.endswith('.bam'):
        return 'BAM'
    elif path.endswith('.cram'):
        return 'CRAM'
    elif path.endswith('.fasta'):
        return 'FASTA'
    elif path.endswith('.fastq'):
        return 'FASTQ'
    elif path.endswith('.vcf'):
        return 'VCF'
    elif path.endswith('.bcf'):
        return 'BCF'
    elif path.endswith('.maf'):
        return 'MAF'
    elif path.endswith('.tbx'):
        return 'TABIX'
    elif path.endswith('.gtf'):
        return 'TABIX'
    elif path.endswith('.gff'):
        return 'TABIX'
    elif path.endswith('.bed'):
        return 'BED'
    elif path.endswith('.bedpe'):
        return 'BEDPE'
    else:
        return None


def validate_filetype(path):
    '''
    Perform a series of validations on your file of interest

    Parameters
    ----------
    path : str
        File path to validate
    '''
    ftype = detect_filetype_from_path(path)
    func_switch = {
        'SAM': validate_sam,
        'BAM': validate_bam,
        'CRAM': validate_cram,
        'FASTA': validate_fasta,
        'FASTQ': validate_fastq,
        'VCF': validate_vcf,
        'BCF': validate_bcf,
        'MAF': validate_maf,
        'TABIX': validate_tabix,
        'BED': validate_bed,
        'BEDPE': validate_bedpe
    }
    return func_switch[ftype](path)


def validate_sam(path):
    '''
    Validate SAM file

    Parameters
    ----------
    path : str
        File to check
    '''
    raise NotImplementedError()


def validate_bam(path):
    '''
    Validate BAM file

    Parameters
    ----------
    path : str
        File to check
    '''
    raise NotImplementedError()


def validate_cram(path):
    '''
    Validate CRAM file

    Parameters
    ----------
    path : str
        File to check
    '''
    raise NotImplementedError()


def validate_fasta(path):
    '''
    Validate FASTA file

    Parameters
    ----------
    path : str
        File to check
    '''
    raise NotImplementedError()


def validate_fastq(path):
    '''
    Validate FASTQ file

    Parameters
    ----------
    path : str
        File to check
    '''
    raise NotImplementedError()


def validate_vcf(path):
    '''
    Validate VCF file

    Parameters
    ----------
    path : str
        File to check
    '''
    raise NotImplementedError()


def validate_bcf(path):
    '''
    Validate BCF file

    Parameters
    ----------
    path : str
        File to check
    '''
    raise NotImplementedError()


def validate_maf(path):
    '''
    Validate MAF file

    Parameters
    ----------
    path : str
        File to check
    '''
    raise NotImplementedError()


def validate_tabix(path):
    '''
    Validate TABIX file

    Parameters
    ----------
    path : str
        File to check
    '''
    raise NotImplementedError()


def validate_bed(path):
    '''
    Validate BED file

    Parameters
    ----------
    path : str
        File to check
    '''
    raise NotImplementedError()


def validate_bedpe(path):
    '''
    Validate BEDPE file

    Parameters
    ----------
    path : str
        File to check
    '''
    raise NotImplementedError()
