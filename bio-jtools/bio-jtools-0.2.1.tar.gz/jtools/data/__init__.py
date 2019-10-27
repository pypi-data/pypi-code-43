DIRNAME_REGEX = '^([0-9]{2})(0?[1-9]|1[012])(0[1-9]|[12]\\d|3[01])_(\\w{6})_(\\d{4})_(A|B)(\\w{9})(.*)?/?$'
FASTQ_FILENAME_REGEX = '^([A-Za-z0-9-_]+)_S([1-9][0-9]?)_L00(\\d)_(I1|R[1-3])_001\\.fastq(\\.gz)?$'
RESERVED_DIRS = ['Reports', 'FASTQs', 'Trimmed', 'Aligned']
RESERVED_FILENAMES = ['README.md', 'cluster.yaml', 'config.tsv', 'Snakefile', 'setup.log']

README_STR = '''# Summary

Date Submitted: {date_sub}
Date Received: {date_rec}
Flowcell ID: {flowcell}

{description}
'''

CLUSTER_STR = '''__default__:
  params: "-q lupiengroup -cwd -V"

'''

SNAKEFILE_STR = '''import pandas as pd
import os.path as path

# =============================================================================
# Configuration
# =============================================================================
CONFIG = pd.read_csv('config.tsv', index_col=False, sep='\\t')
CONFIG = CONFIG.loc[~CONFIG.Sample.str.startswith('#'), :]

REPORT_DIR = 'Reports'
FASTQ_DIR = 'FASTQs'
ALIGN_DIR = 'Aligned'

SAMPLES = CONFIG['Sample'].tolist()
READS = [1, 2]
LANES = [1, 2, 3, 4]
BWT2_IDX = '/cluster/tools/data/genomes/human/hg38/iGenomes/Sequence/Bowtie2Index/genome'
CHRS = ['chr' + str(i) for i in list(range(1, 23)) + ['X', 'Y']]

wildcard_constraints:
    sample = '[A-Za-z0-9-]+',
    lane = '[1-4]',
    read = '[1-2]'

# =============================================================================
# Meta Rules
# =============================================================================
rule all:
    input:
        'rulegraph.png',
        path.join(REPORT_DIR, 'multiqc_report.html'),
        expand(
            path.join(REPORT_DIR, '{{sample}}_L00{{lane}}_R{{read}}_fastqc.zip'),
            sample=SAMPLES,
            lane=LANES,
            read=READS
        ),

rule rulegraph:
    output:
        'rulegraph.png',
    shell:
        'snakemake --rulegraph | dot -Tpng > {{output}}'

# =============================================================================
# Rules
# =============================================================================
# Summaries
# -----------------------------------------------------------------------------
rule fastqc:
    input:
        path.join(FASTQ_DIR, '{{file}}.fastq.gz')
    output:
        path.join(REPORT_DIR, '{{file}}_fastqc.html'),
        path.join(REPORT_DIR, '{{file}}_fastqc.zip')
    params:
        '-o {{}}'.format(REPORT_DIR)
    shell:
        'fastqc {{params}} {{input}}'


rule multiqc:
    input:
        samples = expand(
            path.join(REPORT_DIR, '{{sample}}_fastqc.zip'),
            sample=SAMPLES
        )
    output:
        path.join(REPORT_DIR, 'multiqc_report.html')
    shell:
        'multiqc -f -o {{REPORT_DIR}} {{REPORT_DIR}}'



# Miscellaneous
# -----------------------------------------------------------------------------
rule sort_bam_name:
    input:
        '{{file}}.bam'
    output:
        '{{file}}.name-sorted.bam',
    shell:
        'sambamba sort -t 8 --tmpdir . -n -p -o {{output}} {{input}}'

rule sort_bam:
    input:
        '{{file}}.bam'
    output:
        bam = '{{file}}.sorted.bam',
        idx = '{{file}}.sorted.bam.bai'
    shell:
        'sambamba sort -t 8 --tmpdir . -p {{input}}'

'''

SETUP_STR = '''# Making directories
{mkdir}

# Moving files
{mv}

# Creating reserved files
{res_files}

# Formatting FASTQ filenames
{fastq}

'''