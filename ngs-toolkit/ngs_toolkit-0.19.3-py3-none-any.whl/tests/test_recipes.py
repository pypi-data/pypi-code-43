#!/usr/bin/env python

import os
import sys
import subprocess


def test_ngs_analysis():
    cmd = (
        "PEP=`{exe} -m ngs_toolkit.recipes.generate_project "
        "--sample-input-files True`; "
        "{exe} -m ngs_toolkit.recipes.ngs_analysis $PEP"
    ).format(exe=sys.executable)

    assert os.system(cmd, shell=True) == 0


def test_region_set_frip():
    cmd = (
        "PEP=`{exe} -m ngs_toolkit.recipes.generate_project "
        "--sample-input-files True`; "
        "{exe} -m ngs_toolkit.recipes.region_set_frip $PEP"
    ).format(exe=sys.executable)

    assert os.system(cmd, shell=True) == 0

