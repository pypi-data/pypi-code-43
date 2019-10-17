#!python
import json
import os
import sys
from StringIO import StringIO
import shlex
import subprocess
import time
import argparse
import re
import collections


def add_time(toiltime, walltime, key):
    ret = dict()
    if key in toiltime['job_types'].keys():
        ret['thread'] = toiltime['job_types'][key]['total_number']
        ret['avg'] = toiltime['job_types'][key]['average_time']
        ret['max'] = toiltime['job_types'][key]['max_time']
        ret['total'] = toiltime['job_types'][key]['total_time']
    if (key in walltime.keys() and 'Start' in walltime[key].keys()
            and 'End' in walltime[key].keys()):
        ret['start'] = int(walltime[key]['Start'])
        ret['end'] = int(walltime[key]['End'])
        ret['walltime'] = int(walltime[key]['End']) - int(
            walltime[key]['Start'])
    return {key: ret}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Check Toil run jobStore and output runtime JSON file')
    parser.add_argument(
        'inputLog',
        help="STDERR output from Toil run, with Job Start/End Info.")
    parser.add_argument('jobStore', help="Toil run jobStore pathname.")
    parser.add_argument('outputJSON', help="output JSON file.")
    parser.add_argument(
        '-k', '--keep', action='store_true', help="keep jobStore undeleted.")
    args = parser.parse_args()

    reportJobNames = [
        'BwaIndex', 'BwaShm', 'Map', 'Duplicate', 'SamtoolsIndex',
        'GVC', 'LinearPredict', 'XGBoostPredict', 'BedFilter', 'GenerateVCF',
        'QC', 'QC_Postprocess', 'QC_DefineRegion',
        'Annotation'
    ]  # all jobNames you want to see in output JSON file

    walltime = collections.defaultdict(dict)
    rex = re.compile(r'Runtime\.([^\.]+)\.(Start|End)=(\d+)')
    with open(args.inputLog, 'r') as infile:
        for line in infile:
            matchTime = rex.search(line)
            if matchTime:
                (jobName, typeStr, timestamp) = matchTime.group(1, 2, 3)

                if (not typeStr in walltime[jobName].keys()
                        or (typeStr == 'Start'
                            and timestamp < walltime[jobName][typeStr])
                        or (typeStr == 'End'
                            and timestamp > walltime[jobName][typeStr])):
                    walltime[jobName][typeStr] = timestamp

    # get runtime from jobStore
    stats_cmd = 'toil stats --raw file:' + args.jobStore
    p = subprocess.Popen(
        shlex.split(stats_cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (log, err) = p.communicate()
    if p.returncode != 0:
        sys.stderr.write('ERROR: Cloud not get runtime from jobStore.')
        sys.stderr.write(err)
        exit(1)
    # parse runtime then write our own runtime.json
    toiltime = json.load(StringIO(log))
    runtime = dict()
    # use the earliest job start time as analysis_start_time
    runtime['analysis_start_time'] = 0  # init
    runtime['analysis_runtime'] = toiltime['total_run_time']
    for jobName in reportJobNames:
        runtime.update(add_time(toiltime, walltime,
                                jobName))  # info from jobStore and INFO
        if ('Start' in walltime[jobName].keys() and
            (runtime['analysis_start_time'] == 0
             or runtime['analysis_start_time'] > walltime[jobName]['Start'])):
            runtime['analysis_start_time'] = walltime[jobName]['Start']

    timeJsonFile = args.outputJSON
    with open(timeJsonFile, 'w') as outfile:
        json.dump(runtime, outfile, indent=4)

    # clean jobstore
    if not args.keep:
        subprocess.call(['toil', 'clean', args.jobStore])
