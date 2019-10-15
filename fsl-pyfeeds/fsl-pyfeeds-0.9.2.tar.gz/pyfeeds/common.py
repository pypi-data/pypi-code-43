#!/usr/bin/env python
#
# common.py - Miscellaneous functions
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains some miscellaneous utility functions used throughout
pyfeeds, and made available to test scripts.

.. autosummary::
   :nosignatures:

   printColumns
   findCommonAncestors
   findPathIn
   createSandbox
   loadNumericText
   allBefore
   starmap
   fslbin
   readfsf
   writefsf
"""


from __future__ import print_function
from __future__ import division

import            collections
import            datetime
import            tempfile
import            logging
import            shutil
import            re
import            os
import os.path as op
import numpy   as np


log = logging.getLogger(__name__)


def printColumns(titles, columns):
    """Convenience function which pretty-prints a collection of columns in a
    tabular format.

    :arg titles:  A list of titles, one for each column.

    :arg columns: A list of columns, where each column is a list of strings.
    """

    cols  = []

    for t, c in zip(titles, columns):
        cols.append([t] + list(map(str, c)))

    columns = cols
    colLens = []

    for col in columns:
        maxLen = max([len(r) for r in col])
        colLens.append(maxLen)

    fmtStr = ' | '.join(['{{:<{}s}}'.format(l) for l in colLens])

    titles  = [col[0]  for col in columns]
    columns = [col[1:] for col in columns]

    separator = ['-' * l for l in colLens]

    print(fmtStr.format(*titles))
    print(fmtStr.format(*separator))

    nrows = len(columns[0])
    for i in range(nrows):

        row = [col[i] for col in columns]
        print(fmtStr.format(*row))



def findCommonAncestor(paths):
    """Finds the nearest common ancestor, in the file system hierarchy, of
    all the given paths.
    """

    pathLens  = [len(p) for p in paths]
    template  = paths[np.argmin(pathLens)]
    parents   = template.split(op.sep)[:-1]
    depth     = len(parents)

    while depth > 0:

        path = op.sep.join(parents[:depth])

        for p in paths:
            if not p.startswith(path):
                break
        else:
            break

        depth -= 1

    return op.sep.join(parents[:depth])


def findPathIn(path, base):
    """Searches for the given ``path`` in the given ``base`` directory.

    The search begins with the full ``path``. If ``base/path`` does not
    exist, the leading directory from ``path`` is removed, and the search
    repeated.

    Returns the full path to ``base/path``, or ``None`` if the ``path`` cannot
    be found in ``base``.

    This function is used to search for a benchmark data directory which
    corresponds to a specific test directory. The benchmark data directory
    must have the same folder structure as the base directory of all of the
    tests that pyfeeds is given. But pyfeeds does not necessarily know the
    base test directory. So when pyfeeds needs to find the benchmark data for
    a given test, it uses this function to find it.

    This is easier to explain with an example. Say our benchmark data is
    stored in::

        /opt/pyfeeds/benchmarkData/

    And we want to find the benchmark data for a test stored in::

        /opt/pyfeeds/testSuite/reg/flirt/

    Which is stored in::

        /opt/pyfeeds/benchmarkData/reg/flirt

    This function will iteratively test the following paths until it finds a
    match::

        /opt/pyfeeds/benchmarkData/opt/pyfeeds/testSuite/reg/flirt/
        /opt/pyfeeds/benchmarkData/pyfeeds/testSuite/reg/flirt/
        /opt/pyfeeds/benchmarkData/testSuite/reg/flirt/
        /opt/pyfeeds/benchmarkData/reg/flirt/

    Obviously this is not a foolproof method, but the current design of
    pyfeeds disallows test directories to be unambiguously matched to
    benchmark directories.
    """

    if path.startswith(op.sep):
        path = path[1:]

    while len(path) > 0:

        test = op.join(base, path)

        if op.exists(test):
            return test

        path = op.sep.join(path.split(op.sep)[1:])

    return None


def createSandbox(inputDir, inputs, sandbox=None, symlink=True):
    """Creates a *sandbox* directory which contains symlinks or copies of all
    files in the given list of ``inputs``.

    :arg inputDir: Directory in which the data is located.

    :arg inputs:   A list of paths, specified relative to the ``inputDir``,
                   which should be copied / symlinked into the sandbox.

    :arg sandbox:  Directory in which the sandbox should be created. If
                   ``None``, a temporary directory is created and used.
                   It is up to the caller to remove this directory if
                   necessary.

    :arg symlink:  If ``True`` (the default), the sandbox is created
                   with symlinks to the input data. Otherwise, the
                   input data is copied to the sandbox directory.

    :returns:      The path to the sandbox directory, or ``None`` if
                   ``inputs`` is empty.
    """

    if len(inputs) == 0:
        return None

    if sandbox is None: sandbox = tempfile.mkdtemp(prefix='pyfeeds_')
    else:               sandbox = op.abspath(sandbox)

    log.debug('Creating sandbox: {}'.format(sandbox))

    # We sort input alphabetically,
    # and keep keep track of paths
    # that have already been copied.
    # Sorting ensures that if we have
    # two paths like this:
    #
    # /inputDir/testData/
    # /inputDir/testData/file.nii.gz
    #
    # They will always be ordered such
    # that the shorter one will come
    # first. The code below depends on
    # this ordering.
    inputs = sorted(set(inputs))
    copied = set()

    for src in inputs:

        log.debug('Processing input: {}'.format(src))

        relSrc  = src
        srcName = op.basename(src)
        src     = op.join(inputDir, src)

        if not op.exists(src):
            log.warning('Invalid path: {}'.format(src))
            continue

        # Has the directory in which this input
        # is contained already been copied /
        # linked?
        #
        # Test to see if any of the parent
        # directories of the input have been
        # added to the copied set.
        path          = src
        alreadyCopied = False
        while len(path) != 0:

            path = path.rstrip(op.sep)

            if path in copied:
                alreadyCopied = True
                break

            path = op.dirname(path)

        if alreadyCopied:
            log.debug('Skipping duplicate path: {}'.format(src))
            continue

        # Keep track of all copied / linked files / directoriess
        copied.add(src)

        relSrcDir = op.dirname(relSrc)
        destDir   = op.join(sandbox,  relSrcDir)
        dest      = op.join(destDir,  srcName)

        if not op.exists(destDir):
            os.makedirs(destDir)

        if symlink:
            log.debug('Sym-linking: {} -> {}'.format(src, dest))
            os.symlink(src, dest)

        else:
            log.debug('Copying: {} -> {}'.format(src, dest))

            if op.isdir(src): shutil.copytree(src, dest)
            else:             shutil.copy(    src, dest)

    return sandbox


def loadNumericText(filename):
    """Attempts to load any and all numbers from the given plain text file.
    Returns all found numbers as a ``numpy`` array.
    """

    # http://perldoc.perl.org/perlretut.html#Building-a-regexp
    # http://stackoverflow.com/a/385597
    numberPattern = r'[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'
    numberPattern = re.compile(numberPattern)

    def stof(s):
        try:               return float(s)
        except ValueError: return np.nan

    with open(filename, 'rt') as f:
        text    = f.read()
        numbers = numberPattern.findall(text)
        numbers = [stof(n) for n in numbers]

        return np.array(numbers)


def allBefore(path, timeThres):
    """Recursively checks the last-modified time of every file in the given
    ``path`` against the given ``timeThres``.

    :returns:       ``True`` if no files were modified after the
                    ``timeThres``, ``False`` otherwise.

    :arg path:      Path to a directory or file.

    :arg timeThres: ``datatime`` object containing the last modified
                    threshold.
    """

    mtime = datetime.datetime.fromtimestamp(op.getmtime(path))

    if mtime >= timeThres:
        return False

    if op.isdir(path):
        for p in os.listdir(path):
            if not allBefore(op.join(path, p), timeThres):
                return False

    return True


def starmap(func):
    """This function is used as a decorator on functions which
    are passed to the ``multiprocessing.Pool.map`` function, to allow
    us to pass un-expanded argument lists to the function being
    executed.

    .. note:: This function is part of the standard Python library
              in Python 3.3 and newer, but does not exist in older
              versions.
    """
    def wrapper(args):
        return func(*args)
    return wrapper


def fslbin(name):
    """Returns an absolute path to the named FSL command. """
    return op.join(os.environ["FSLDIR"], "bin", name)


def readfsf(filename, keys):
    """Reads the given ``keys`` from a FEAT ``fsf`` configuration file. """
    if not isinstance(keys, collections.Sequence):
        keys = [keys]

    values = {}

    with open(filename, 'rt') as f:
        for line in f:

            if not line.startswith('set '):
                continue
            line = line.split()
            k    = line[1]
            v    = ' '.join(line[2:])
            if k in keys:
                values[k] = v
    return [values[key] for key in keys]


def writefsf(filename, keys, values):
    """Writes the given ``keys`` and corresponding ``values`` to a FEAT
    ``fsf`` configuration file.
    """

    if not isinstance(keys,   collections.Sequence): keys   = [keys]
    if not isinstance(values, collections.Sequence): values = [values]

    if len(keys) != len(values):
        raise ValueError('len(keys) != len(values)')

    with open(filename, 'at') as f:
        for k, v in zip(keys, values):
            f.write('\nset {} {}'.format(k, v))
