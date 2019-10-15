#!/usr/bin/env python
#
# __init__.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import os
import sys
import os.path as op
import contextlib
import tempfile

from io import StringIO

from pyfeeds import main

import argparse


class CaptureStdout(object):
    """Context manager which captures stdout and stderr. """

    def __init__(self):
        self.reset()

    def reset(self):
        self.__mock_stdout = StringIO('')
        self.__mock_stderr = StringIO('')

    def __enter__(self):
        self.__real_stdout = sys.stdout
        self.__real_stderr = sys.stderr

        sys.stdout = self.__mock_stdout
        sys.stderr = self.__mock_stderr


    def __exit__(self, *args, **kwargs):
        sys.stdout = self.__real_stdout
        sys.stderr = self.__real_stderr

        if args[0] is not None:
            print('Error')
            print('stdout:')
            print(self.stdout)
            print('stderr:')
            print(self.stderr)

        return False

    @property
    def stdout(self):
        self.__mock_stdout.seek(0)
        return self.__mock_stdout.read()

    @property
    def stderr(self):
        self.__mock_stderr.seek(0)
        return self.__mock_stderr.read()


@contextlib.contextmanager
def tempdir():
    prevdir = os.getcwd()
    with tempfile.TemporaryDirectory() as td:
        try:
            os.chdir(td)
            yield td
        finally:
            os.chdir(prevdir)


def makepaths(paths):
    for path in paths:
        dirname = op.dirname(path)
        if dirname != '':
            os.makedirs(dirname, exist_ok=True)
        with open(path, 'w'):
            pass


def maketest(filename, returnCode=0, inputs=None, outputs=None, stdout=None):

    if outputs is None:
        outputs = []
    if stdout is None:
        stdout = []

    dirname = op.dirname(filename)

    os.makedirs(dirname, exist_ok=True)

    with open(filename, 'wt') as f:
        f.write('#!/bin/bash\n')
        f.write('outdir=$1\n')

        for output in outputs:
            f.write('mkdir -p $(dirname $outdir/{})\n'.format(output))
            f.write('touch $outdir/{}\n'.format(output))

        for line in stdout:
            f.write('echo "{}"\n'.format(line))

        f.write('exit {}\n'.format(returnCode))


    if inputs is not None:
        with open(op.join(dirname, 'feedsInputs'), 'wt') as f:
            for i in inputs:
                f.write(i + '\n')


def makepyfeeds(**kwargs):
    args = argparse.Namespace(**kwargs)
    cfg  = argparse.Namespace()
    return main.Pyfeeds(args, cfg)
