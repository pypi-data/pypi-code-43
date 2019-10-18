#!/usr/bin/env python

import os

from ngs_toolkit.utils import download_file


def test_download_file():
    url = 'https://egg2.wustl.edu/roadmap/data/byFileType/chromhmmSegmentations'
    url += '/ChmmModels/coreMarks/jointModel/final/E001_15_coreMarks_dense.bed.gz'
    output_file = "https_file.gz"
    chunk_size = 1024
    download_file(url, output_file, chunk_size)
    assert os.stat(output_file).st_size == 4822100
    url = "ftp://ftp.ensembl.org/pub/release-97/gtf/homo_sapiens/README"
    output_file = "ftp_file.txt"
    chunk_size = 1024
    download_file(url, output_file, chunk_size)
    assert os.stat(output_file).st_size == 10093
