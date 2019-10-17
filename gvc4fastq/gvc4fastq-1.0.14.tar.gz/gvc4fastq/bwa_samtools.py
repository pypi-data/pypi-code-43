from toil.common import Toil
from toil.job import Job
from collections import OrderedDict

import pwd
import getpass
import argparse
import os
import sys
import json
import docker
import itertools
import time
import fcntl
import sortbamInterface
from runner.runner import docker_runner, decorator_wrapt, docker_runner_method


def lock(fileName):
    file_lock = open(fileName, 'w')
    fcntl.lockf(file_lock, fcntl.LOCK_EX)  # exclusive lock
    return file_lock


def unlock(fileName):
    fcntl.lockf(fileName, fcntl.LOCK_UN)
    fileName.close()


class Map(Job):
    @decorator_wrapt
    def __init__(self, R1file, R2file, bwa_threads, ref, samtoolst, sampleName,
                 outpath, image, volumes, *args, **kwargs):
        self.R1file = R1file
        self.R2file = R2file
        self.bwa_threads = bwa_threads
        self.ref = ref
        self.samtoolst = samtoolst
        self.outpath = outpath
        self.sampleName = sampleName
        self.outfile = self.outpath + '/' + self.sampleName + '.sort.bam'
        self.image = image
        self.volumes = volumes

        self.commandLine = [
            'bash', '/bin/bwa_samtools.sh', self.R1file, self.R2file,
            self.bwa_threads, self.ref, self.samtoolst, self.outpath,
            self.outfile
        ]
        super(Map, self).__init__(*args, **kwargs)

    @docker_runner('Map')
    def run(self, fileStore):
        return self.commandLine

    def get_bam_name(self):
        return self.outfile


class BwaIndex(Job):
    @decorator_wrapt
    def __init__(self, ref, image, volumes, *args, **kwargs):
        self.ref = ref
        self.image = image
        self.volumes = volumes
        self.LOCK_FILE = '/tmp/index_lock.' + os.path.basename(self.ref)
        self.commandLine = ['bwa', 'index', self.ref]
        super(BwaIndex, self).__init__(*args, **kwargs)

    def run(self, fileStore):
        file_lock = lock(self.LOCK_FILE)
        if (os.path.exists(ref + '.bwt') and os.path.exists(ref + '.pac')
                and os.path.exists(ref + '.sa')
                and os.path.exists(ref + '.amb')) is False:
            docker_runner_method(self, self.commandLine, "BwaIndex",
                                 self.image, self.volumes)
        unlock(file_lock)


class BwaShm(Job):
    def __init__(self, ref, image, volumes, *args, **kwargs):
        self.ref = ref
        self.image = image
        self.volumes = volumes

        self.refName = os.path.basename(self.ref)
        self.LOCK_FILE = '/tmp/share_memory_lock.' + self.refName
        self.READY_FILE = '/tmp/share_memory_ready.' + self.refName
        self.commandLine = ['bwa', 'shm', self.ref]
        super(BwaShm, self).__init__(*args, **kwargs)

    # XXX: one single server
    def run(self, fileStore):
        if os.path.exists(self.READY_FILE) is False:
            file_lock = lock(self.LOCK_FILE)
            if os.path.exists(self.READY_FILE) is False:
                docker_runner_method(
                    self,
                    self.commandLine,
                    "BwaShm",
                    self.image,
                    self.volumes,
                    ipc_mode="host")
                os.mknod(self.READY_FILE)
            unlock(file_lock)


class Duplicate(Job):
    @decorator_wrapt
    def __init__(self, bam, dupbam, image, volumes, threads, *args, **kwargs):
        self.bam = bam
        self.dupbam = dupbam
        self.commandLine = ['duplicate', '-n', threads, bam, self.dupbam]
        self.volumes = volumes
        self.image = image

        super(Duplicate, self).__init__(*args, **kwargs)

    def run(self, fileStore):
        docker_runner_method(self, self.commandLine, "Duplicate", self.image,
                             self.volumes)
        # os.remove(self.bam)

    def get_bam_name(self):
        return self.dupbam


class IndexBam(Job):
    @decorator_wrapt
    def __init__(self, bam, image, volumes, threads='1', *args, **kwargs):
        self.image = image
        self.volumes = volumes
        self.commandLine = ['samtools', 'index', '-@', threads, bam]
        super(IndexBam, self).__init__(*args, **kwargs)

    @docker_runner('SamtoolsIndex')
    def run(self, fileStore):
        return self.commandLine


def cmd_parser(absPath):
    parser = Job.Runner.getDefaultArgumentParser()
    parser.add_argument('--R1', help="R1 fastq file"),
    parser.add_argument('--R2', help="R2 fastq file"),
    parser.add_argument('--ref', help="references"),
    parser.add_argument('--outpath', help='The output folder'),
    parser.add_argument('--sampleName', help='sample name'),
    parser.add_argument('--version', type=argparse.FileType('r')),
    parser.add_argument('--volumes', type=argparse.FileType('r')),
    parser.add_argument('--threads', type=argparse.FileType('r'))
    return parser.parse_args()


def mapping_pipeline(root, R1file, R2file, ref, outpath, sampleName, version,
                     volumes, max_threads):
    bwa_threads = int(round(max_threads * 0.75))
    sort_threads = int(round(max_threads * 0.75))
    dup_threads = 4
    index_threads = int(round(max_threads * 0.5))
    if (os.path.exists(ref + '.bwt') and os.path.exists(ref + '.pac')
            and os.path.exists(ref + '.sa')
            and os.path.exists(ref + '.amb')) is False:
        BwaIndex_job = BwaIndex(ref, version['gmap'], volumes)
        root.addChild(BwaIndex_job)
    else:
        BwaIndex_job = root
    BwaShm_job = BwaShm(ref, version['gmap'], volumes)
    BwaIndex_job.addChild(BwaShm_job)

    map_job = Map(
        R1file,
        R2file,
        str(bwa_threads),
        ref,
        str(sort_threads),
        sampleName,
        outpath,
        version['gmap'],
        volumes,
        cores=int(max_threads),
        memory='8G')
    BwaShm_job.addChild(map_job)

    i_sort = sortbamInterface.SortBamInterface()
    i_sort.append_bam(map_job.get_bam_name())
    sort_index_job = IndexBam(
        map_job.get_bam_name(),
        version['gmap'],
        volumes,
        threads=str(index_threads),
        cores=int(index_threads),
        memory='8G')
    map_job.addChild(sort_index_job)
    dup_job = Duplicate(
        map_job.get_bam_name(),
        outpath + '/' + sampleName + '.sort.dup.bam',
        version['duplication'],
        volumes,
        '12',
        cores=int(dup_threads))
    sort_index_job.addChild(dup_job)
    index_job = IndexBam(
        dup_job.get_bam_name(),
        version['gmap'],
        volumes,
        threads=str(index_threads),
        cores=int(index_threads))
    dup_job.addChild(index_job)
    return dup_job.get_bam_name()


if __name__ == "__main__":
    absPath = os.path.abspath(os.path.dirname(sys.argv[0]))
    options = cmd_parser(absPath)
    version = json.load(options.version, object_pairs_hook=OrderedDict)
    volumes = json.load(options.volumes, object_pairs_hook=OrderedDict)
    threads = json.load(options.threads, object_pairs_hook=OrderedDict)
    start_job = Job()
    map_job = mapping_pipeline(start_job, options.R1, options.R2, options.ref,
                               options.outpath, options.sampleName, version,
                               volumes, threads)

    with Toil(options) as toil:
        if not toil.options.restart:
            toil.start(start_job)
        else:
            toil.restart()
