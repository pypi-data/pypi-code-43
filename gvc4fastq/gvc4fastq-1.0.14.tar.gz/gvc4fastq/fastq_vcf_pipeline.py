import os
import sys
from . import bwa_samtools
from gvc4bam import license_job
from gvc4bam import gvc_vcf_pipeline  as bam_vcf_pipeline
from gvc4bam import gvc_pipeline
import copy
from collections import namedtuple
from toil.job import Job
from toil.common import Toil
import docker
import re
import gzip
from collections import OrderedDict
import subprocess
import shlex
import json
import multiprocessing
import argparse


def check_dir_volume(file_path):
    if os.path.exists(file_path) is False:
        print(file_path + ' is not found')
        sys.exit(-1)


# ['L1.read1.fq,L2.read1.fq','L1.read2.fq,L2.read2.fq']
def check_fastq_(*reads_vals):
    for reads_group in reads_vals:
        for reads_file in reads_group.split(','):
            if os.path.exists(reads_file) is False:
                print(reads_file + 'is not found')
                sys.exit(-2)


def get_reads_length(*reads_vals):
    choice_length = [100, 150]
    read_length = list()
    for reads_group in reads_vals:
        for reads_file in reads_group.split(','):
            if re.search(".gz$", reads_file):
                open_func = gzip.open
            else:
                open_func = open

            with open_func(reads_file) as F:

                for linenum, line_str in enumerate(F):
                    if linenum == 1:
                        read_length.append(len(line_str))
                        break
    arv_len = sum(read_length)/len(read_length)
    return min(choice_length, key=lambda x: abs(x-arv_len))


def cmd_parser(absPath):
    parser = Job.Runner.getDefaultArgumentParser()
    parser.add_argument(
        'input_json',
        help='The json file stores names and paths of both normal and tumor samples.'
        + '\n' +
        'eg: { "N": { "R1": ["/disk/N_R1_1.fastq.gz, /disk/N_R1_2.fastq.gz"],'
        '"R2":["/disk/N_R2_1.fastq.gz,/disk/N_R2_2.fastq.gz"]},'
        '"T": {"R1":["/disk/T_R1_1.fastq.gz,/disk/T_R1_2.fastq.gz"],'
        '"R2":["/disk/T_R2_1.fastq.gz,/disk/T_R2_2.fastq.gz"]}}')
    parser.add_argument('reference', help='The reference fasta file')
    parser.add_argument('outpath', help='The output folder')
    parser.add_argument(
        '--dbsnp',
        help="The Single Nucleotide Polymorphism Database(dbSNP) file",
        required=True)
    parser.add_argument(
        '--bed',
        help="""BED file for WES or Panel analysis. It should be a TAB delimited file
with at least three columns: chrName, startPosition and endPostion""")
    parser.add_argument(
        '--segmentSize',
        type=int,
        help="Chromosome segment size for each GVC job, set to 100000000 (100MB) or larger for better performance. Default is to run only one GVC job.")
    parser.add_argument(
        '--gvc_lib',
        help="GVC library folder")
    parser.add_argument('--strategy', choices=['WES', 'WGS', 'Panel'],help='Switch algorithm for WES, Panel or WGS analysis')
    parser.add_argument(
        '--mutantType',
        help="Getting Germline mutation or Somatic mutaion",
        choices=['Somatic', 'Germline'],
        action='append',
        default=[])
    parser.add_argument('--CNV',action='store_true',default=False,help='calculate and output CNV simultaneously')
    parser.add_argument('--SV',action='store_true',default=False,help='calculate and output SV simultaneously')
    parser.add_argument(
        '--sample_name', help="Name of the sample to be analyzed.", default='sample_name')
    parser.add_argument('--rmtmp',action='store_true',default=False,help='remove tempelate file')
    parser.add_argument(
        '--region',
        help=argparse.SUPPRESS
    )
    return parser.parse_args()


input_setting = namedtuple(
    'input_setting', ['version', 'input_data'])


def input_loads_json(filename):
    with open(filename) as F:
        return json.load(F, object_pairs_hook=OrderedDict)


def input_phaser(gvc_lib, input_json):
    l_paths = map(lambda x: os.path.join(gvc_lib, x), [
                  'version.json'])
    l_paths.append(input_json)
    map(check_dir_volume, l_paths)
    return input_setting(*map(input_loads_json, l_paths))


def pairs_sample_bam(bam_list, settings):
    return dict(zip(settings.input_data, map(lambda x: [x], bam_list)))


def get_all_reads(input_data):
    all_reads = list()
    for paired_reads in input_data.values():
        all_reads += paired_reads['R1']
        all_reads += paired_reads['R2']
    return all_reads


def get_model_path(gvc_lib_path,choice_length): 
    return '{}/Model/PE{}'.format(gvc_lib_path,choice_length)

def main():
    absPath = os.path.abspath(os.path.dirname(__file__))
    options = cmd_parser(absPath)
    settings = input_phaser(options.gvc_lib, options.input_json)
    for paired_reads in settings.input_data.values():
        check_fastq_(paired_reads['R1'][0], paired_reads['R2'][0])
    all_reads = get_all_reads(settings.input_data)

    max_cores = int(options.maxCores) if options.maxCores else multiprocessing.cpu_count()
    choice_len = get_reads_length(*all_reads)
    model_path = get_model_path(options.gvc_lib,choice_len)

    limit_regions = gvc_pipeline.get_regions_file(options.region)
    if options.bed:
        volumes = bam_vcf_pipeline.get_dynamic_volumes(options.dbsnp,options.outpath,options.reference,options.bed,options.gvc_lib,model_path,*all_reads)
    else:
        volumes = bam_vcf_pipeline.get_dynamic_volumes(options.dbsnp,options.outpath,options.reference,options.gvc_lib ,model_path,*all_reads)
    
    check_volumes = copy.deepcopy(volumes)
    check_volumes[options.gvc_lib] = {
        "bind": "/Genowis",
        "mode": "rw"
    }
    start_job = license_job.verify_license(settings.version['xgboost'],check_volumes)
    bam_list = list()
    for sample_name, paired_reads in settings.input_data.iteritems():
        bam_list.append(bwa_samtools.mapping_pipeline(start_job, paired_reads['R1'][0], paired_reads['R2'][0],
                                                      options.reference, options.outpath, sample_name, settings.version, volumes, max_cores))
    
    start_job = start_job.encapsulate()
    dict_group_info = pairs_sample_bam(bam_list, settings)
    start_job = bam_vcf_pipeline.bam_vcf_pipeline(start_job, options.gvc_lib, options.reference, options.dbsnp, options.strategy,
                                                  options.bed,
                                                  options.outpath, dict_group_info, options.mutantType, options.segmentSize,
                                                  options.sample_name,model_path, CNV_enable=options.CNV,SV_enable=options.SV,check_bam=False,volumes=volumes,rm_temp=options.rmtmp,limit_regions=limit_regions)
    #print (options.maxCores)

    with Toil(options) as toil:
        if not toil.options.restart:
            toil.start(start_job)
        else:
            toil.restart()


if __name__ == "__main__":
    main()
