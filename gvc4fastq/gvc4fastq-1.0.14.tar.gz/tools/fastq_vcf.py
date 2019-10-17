#!/usr/bin/python
import argparse
import sys
import os
import subprocess
import time
import json
import argparse
from collections import OrderedDict


def QC_common_time(runtime, check_type, QC_types=['QC']):
    return map(lambda x: runtime[x][check_type], QC_types)


def QC_time_def(runtime):
    return QC_common_time(runtime, 'total')


def QC_thread_def(runtime):
    return QC_common_time(runtime, 'thread')


def cmdPhase(absPath):
    parser = argparse.ArgumentParser(description="Bam_Vcf")
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
        help="The Single Nucleotide Polymorphism Database(dbSNP) file", required=True)
    parser.add_argument(
        '--bed',
        help="""BED file for WES or Panel analysis. It should be a TAB delimited file
with at least three columns: chrName, startPosition and endPostion""")
    parser.add_argument(
        '--segmentSize',
        help="Chromosome segment size for each GVC job, set to 100000000 (100MB) or larger for better performance. Default is to run only one GVC job.")
    parser.add_argument(
        '--gvc_lib',
        help="GVC library folder",
        required=True)
    parser.add_argument(
        '--strategy', choices=['WGS', 'WES', 'Panel'], help='Switch algorithm for WES, Panel or WGS analysis', required=True)
    parser.add_argument(
        '--mutantType',
        help="Switch algorithm for germline or somatic mutation detection",
        choices=['Somatic', 'Germline'],
        action='append',
        required=True,
        default=[])
    parser.add_argument('--region', help=argparse.SUPPRESS)
    parser.add_argument(
        '--sample_name', help="The Sample name", required=True)
    parser.add_argument(
        '--maxMemory', help="The maximum amount of memory to request from the batch" + '\n' +
        "system at any one time, eg: 32G.")
    parser.add_argument(
        '--maxCores', help="The maximum number of CPU cores to request from the batch" + '\n' +
        "system at any one time, eg: 8.")
    parser.add_argument('--CNV', action='store_true', default=False,
                        help='calculate and output CNV simultaneously')
    parser.add_argument('--SV', action='store_true', default=False,
                        help='calculate and output SV simultaneously')
    return parser.parse_args()
#


def subcommandlie(absPath, options):
    commandLine = ['python', '-m' + 'gvc4fastq.fastq_vcf_pipeline', options.outpath + '/jobStore', options.input_json, options.reference,
                   options.outpath]
    if options.dbsnp:
        commandLine.extend(['--dbsnp', options.dbsnp])
    if options.bed:
        commandLine.extend(['--bed', options.bed])
    if options.segmentSize:
        commandLine.extend(['--segmentSize', options.segmentSize])
    if options.maxMemory:
        commandLine.extend(['--maxMemory', options.maxMemory])
    if options.maxCores:
        commandLine.extend(['--maxCores', options.maxCores])
    if options.region:
        commandLine.extend(['--region', options.region])
    if options.CNV:
        commandLine.extend(['--CNV'])

    if options.SV:
        commandLine.extend(['--SV'])

    for mutype in options.mutantType:
        commandLine.extend(['--mutantType', mutype])
    commandLine.extend(['--gvc_lib', options.gvc_lib, '--strategy', options.strategy, '--sample_name', options.sample_name, '--clean=never',
                        '--stats', '--rmtmp'])
    return commandLine


if __name__ == "__main__":
    absPath = os.path.abspath(os.path.dirname(sys.argv[0]))
    options = cmdPhase(absPath)
    #abspath = os.path.dirname(os.path.abspath(__file__)) + '/'
    commandLine = subcommandlie(absPath, options)
    logpath = os.path.join(options.outpath, 'logFile')
    runjson = os.path.join(options.outpath, 'runtime.json')
    STDERR = open(logpath, 'w')
    Start_time = time.time()
    #
    proc1 = subprocess.Popen(commandLine, stderr=STDERR)
    if proc1.wait() != 0:
        with open(logpath) as flog:
            sys.stderr.writelines(flog.readlines())
        sys.exit(-3)
    cmd2 = ['python', absPath + '/check_runtime.py', logpath, options.outpath + '/jobStore',
            runjson]
    proc2 = subprocess.Popen(cmd2, stderr=STDERR)
    if proc2.wait() != 0:
        with open(logpath) as flog:
            sys.stderr.writelines(flog.readlines())
        sys.exit(-4)
    End_time = time.time()
    # print "End_time:", End_time
    with open(runjson) as fp:
        runtime = json.load(fp, object_pairs_hook=OrderedDict)

    QC_total_time = QC_time_def(runtime)
    QC_threads = QC_thread_def(runtime)

    with open(os.path.join(options.gvc_lib, 'thread.json')) as F:
        thread_dict = json.load(F, object_pairs_hook=OrderedDict)
    print("Runtime:{elasped_time}(s)".format(
        elasped_time=str(End_time - Start_time)))
    print("BWA: Jobs={jobs} ,Threads={thread} ,Total_time={total}(s)".format(
        jobs=runtime['Map']['thread'], thread=thread_dict['mapping']['bwa'], total=runtime['Map']['total']))
    print("Duplicate: Jobs={jobs} ,Threads={thread} ,Total_time: {total}(s)".format(
        jobs=runtime['Duplicate']['thread'], thread=thread_dict['samtools']['duplicate'], total=runtime['Duplicate']['total']))
    print("GVC: Jobs={jobs} ,Threads={thread} ,Total_time: {total}(s)".format(
        jobs=runtime['GVC']['thread'], thread=1, total=runtime['GVC']['total']))
    print("QC: Jobs={jobs} ,Threads={thread} ,Total_time: {total}(s)".format(
        jobs=round(sum(
            QC_threads) / len(QC_threads)), thread=5, total=sum(QC_total_time)))
    if os.path.exists(runjson):
        os.remove(runjson)
    if os.path.exists(logpath):
        os.remove(logpath)
