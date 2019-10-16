#!/usr/bin/env python
#
# evaluate.py - Pyfeeds test evaluation logic
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains the :func:`evaluateTest` function, and other functions
used for evaluating the results of a pyfeeds test.


All available evaluation routines are defined in this module, and are
identified by their name - any function with a name that begins in ``eval``,
but not ``evaluate``, is considered to be an evaluation routine.


All evaluation routines must accept two parameters, which are the names of two
files to be compared.


Evaluation routines ending with the word ``Group`` are routines which accept
two groups of files, and evaluate the groups as a whole.


All evaluation routines must return a numeric value, where 0 indicates that
the files are identical, and non-0 indicates that the files are different.
"""

from __future__ import print_function
from __future__ import division

import              logging
import              fnmatch
import              glob
import              sys
import              os
import os.path   as op
import functools as ft

import numpy     as np
import nibabel   as nib

from . import common
from . import hashing


log = logging.getLogger(__name__)


def compareDirs(pyf):
    """The ``compare`` command. Compares the ``inputDir`` against the
    ``benchmarkDir`` using the :func:`compareAllFiles` function.
    """
    compareAllFiles(pyf, None, pyf.inputDir, pyf.benchmarkDir, pyf.outputFile)


def listRoutines():
    """Returns a list containing the names of all available evaluation
    routines.
    """

    thismod  = sys.modules[__name__]
    routines = []

    for attr in thismod.__dict__.keys():
        if attr.startswith('eval') and not attr.startswith('evaluate'):
            routines.append(attr)

    return routines


def isGroupRoutine(rname):
    """Returns ``True`` if the specified routine is a file group evaluation
    routine, ``False``otherwise.
    """
    return rname.endswith('Group')


def evaluateTest(pyf, test, retcode, outputDir, benchmarkDir):
    """Evaluate the given :class:`.Test` instance.

    The following rules are used in evaluating a test:

    1. If the test returns non-0, then it fails.

    2. If the test is in the ``selfEval`` list, then it passes or fails based
       on its return code.

    3. If there is no benchmark data for the test, then it passes or fails
       based on its return code.

    4. Otherwise, the test is evaluated by comparing every file in its
       benchmark data with the corresponding file in the test output.
       This is done by the :func:`compareAllFiles` function.

    :arg pyf:          The :class:`.Pyfeeds`
    :arg test:         The :class:`.Test` instance to be evaluated
    :arg retcode:      Return code of the test process
    :arg outputDir:    Directory containing the test output
    :arg benchmarkDir: Directory containing the benchmark data for the test
                       (or ``None`` if this test has no benchmark data).
    """

    # Rule 1: If a test returns non-0, that
    #         means it failed
    if retcode != 0:
        log.debug('Test {} returned non-zero - failing'.format(test.name))
        return False

    # Rule 2: If the test is in the self_eval
    #         list, this means that it evaluated
    #         itself. It eturned 0, so it passes.
    if isInSelfEval(pyf, test):
        log.debug('Test {} is in selfEval - passing'.format(test.name))
        return True

    if benchmarkDir is None:
        log.debug('Test {} has no benchmark data - passing'.format(test.name))
        return True

    # Rule 4. For every file in the benchmark
    #         data, make sure there is a
    #         corresponding file in the test
    #         output, and make sure it matches
    outFile = op.join(outputDir, 'feedsResults.log')
    log.debug('Test {}: evaluating against benchmark data'.format(test.name))
    return compareAllFiles(pyf, test, outputDir, benchmarkDir, outFile)


def getEvaluationRoutines(pyf, filename):
    """Searches for evaluation routines suitable for testing the given
    ``filename``.

    :returns: A list of tuples, each containing:

                - An evaluation routine function
                - The name of the function

              Or ``[]`` if there are no routines to test the file.
    """

    thismod = sys.modules[__name__]
    matches = {}

    for pattern, rnames in pyf.evalRoutines.items():
        if fnmatch.fnmatch(filename, pattern):
            rfuncs           = [getattr(thismod, n) for n in rnames]
            rfuncs           = [ft.update_wrapper(ft.partial(f, pyf), f)
                                for f in rfuncs]
            routines         = list(zip(rnames, rfuncs))
            matches[pattern] = routines

    # if the file matched multiple patterns,
    # use the longest one, as it is probably
    # the most specific
    routines = []
    if len(matches) > 0:
        routines = matches[max(matches, key=len)]

    return routines


def getFileGroup(pyf, filename):
    """Determines whether the specified file is part of a file group.

    :returns: A tuple containing:

                - A list of all files that are in the group

                - The file patterns in the matched group, or ``None`` if the
                  file is not part of a group.
    """

    filename = op.abspath(filename)
    group    = None

    # find a file group which
    # matches the given file
    for g in pyf.fileGroups:
        for pat in g:

            # All files in a group must
            # be in the same directory
            if fnmatch.fnmatch(op.basename(filename), pat):
                group = g
                break

    if group is None:
        return [filename], None

    dirname  = op.dirname(filename)
    allFiles = []

    for pat in group:
        hits = glob.glob(op.join(dirname, pat))

        for hit in hits:
            hit = op.abspath(hit)
            if hit not in allFiles:
                allFiles.append(hit)

    return list(sorted(allFiles)), tuple(group)


def isInSelfEval(pyf, test):
    """Returns ``True`` if the given :class:`.Test` instance is in the
    ``selfEval`` list, indicating that it has evaluated itself.
    """
    testDir = test.testDir
    matches = [testDir.endswith(p) for p in pyf.selfEval]
    return any(matches)


def isInExcludeList(pyf, filename):
    """Returns ``True`` if the given filename matches any patterns
    in the ``exclude`` list, indicating that it should not be evaluated.
    """
    matches = [fnmatch.fnmatch(filename, p) for p in pyf.exclude]
    return any(matches)


def getTolerance(pyf, filename):
    """Returns an error tolerance to use when evaluating the given
    ``filename`` - either a tolerance in the ``tolerances`` list, or
    the ``defaultTolerance``.
    """
    for pattern, tol in pyf.tolerances.items():
        if fnmatch.fnmatch(filename, pattern):
            return tol

    return pyf.defaultTolerance


def compareAllFiles(pyf, test, outputDir, benchmarkDir, logFile=None):
    """Evaluate the files generated by the given :class:`.Test` instance.

    Walks through the ``benchmarkDir`` comparing every file in it with the
    corresponding file in the ``outputDir``.

    If ``logFile`` is not provided, the output is printed to standard out.
    """

    results         = []
    finalResult     = True
    benchmarks      = []
    groupsEvaluated = {}

    for base, dirs, filenames in os.walk(benchmarkDir):
        filenames = [op.join(base, f) for f in filenames]
        benchmarks.extend(filenames)

    # Loop through every file in the benchmark directory
    for benchmark in benchmarks:

        relbenchmark      = op.relpath(benchmark, benchmarkDir)
        testfile          = op.join(outputDir, relbenchmark)
        routines          = getEvaluationRoutines(pyf, benchmark)
        tolerance         = getTolerance(pyf, benchmark)
        groupfiles, group = getFileGroup(pyf, benchmark)

        # Skip files which match a
        # pattern in the exclude list
        if isInExcludeList(pyf, benchmark):
            results.append((relbenchmark, 'EXCLUDE', None, None, None))
            continue

        # Skip files which do not match
        # a pattern in the evalRoutines
        # list
        if len(routines) == 0:
            results.append((relbenchmark, 'SKIP', None, None, None))
            continue

        # Fail files which exist in the
        # benchmark data, but do not exist
        # in the test output
        if not op.exists(testfile):
            results.append((relbenchmark, 'FAIL', 'file_missing', 0, 0))
            continue

        # Otherwise, test the file. If
        # any evaluation routine generates
        # a value above the tolerance,
        # the test fails for this file.
        try:

            for rname, rfunc in routines:

                # if this is a file group evaluation
                # routine, retrieve all other files
                # that are part of the group
                if isGroupRoutine(rname):

                    # this file group has already
                    # been evaluated. Skip the
                    # evaluation routine, and return
                    # the previously calculated
                    # result.
                    if (rname, group) in groupsEvaluated:

                        def rfunc_cached(*a):
                            error = groupsEvaluated[rname, group]
                            log.debug('Using saved group evaluation '
                                      'results (%s) for %s (group: %s): '
                                      '%0.2f', rname, relbenchmark, group,
                                      error)
                            return error
                        rfunc = ft.update_wrapper(rfunc_cached, rfunc)

                    rargs = [getFileGroup(pyf, testfile)[0], groupfiles]

                else:
                    rargs = [testfile, benchmark]

                error       = rfunc(*rargs)
                result      = error <= tolerance
                finalResult = finalResult and result

                log.debug('%s: %s - %s', testfile, rfunc.__name__, error)

                if result: status = 'PASS'
                else:      status = 'FAIL'

                # Cache results for file group evaluations,
                # so we don't unnecessarily re-evaluate them
                if isGroupRoutine(rname) and \
                   (rname, group) not in groupsEvaluated:
                    log.debug('Saving group evaluation results (%s) '
                              'for %s (group: %s): %0.2f',
                              rname, relbenchmark, group, error)
                    groupsEvaluated[rname, group] = error

                results.append((relbenchmark, status, rname, error, tolerance))

        except Exception:
            log.error('Error evaluating {}'.format(relbenchmark),
                      exc_info=True)
            results.append((relbenchmark, 'ERROR', rname, None, tolerance))
            finalResult = False

    # Every file that gets tested is added to
    # a log file with a CSV format:
    #
    # file, status, routineName, error, tolerance
    def fmtlog(fname, status, routine, error, tolerance):
        if routine   is None: routine   = 'none'
        if error     is None: error     = np.nan
        if tolerance is None: tolerance = np.nan
        fields = [fname,
                  status,
                  routine,
                  '{:0.6g}'.format(error),
                  '{:0.6g}'.format(tolerance)]

        return '{}'.format(','.join(fields))

    def sortkey(result):
        status = result[1]
        error  = result[3]

        statuswt = {'ERROR'   : 500,
                    'FAIL'    : 100,
                    'PASS'    : 50,
                    'SKIP'    : 10,
                    'EXCLUDE' : 1}[status]

        if error is None:
            error = 1
        return statuswt + error

    lines = ['FILE,RESULT,ROUTINE,ERROR,TOLERANCE']
    # sort by error value
    for result in reversed(sorted(results, key=sortkey)):
        lines.append(fmtlog(*result))

    if logFile is not None:
        with open(logFile, 'wt') as f:
            for line in lines:
                f.write(line + '\n')
    else:
        for line in lines:
            print(line)

    return finalResult


def evalHeader(pyf, testfile, benchmark, alldims=True):
    """Evaluation routine which compares the header fields of two NIFTI
    images.

    Returns 0 if they all match, 1 otherwise.
    """

    img1 = pyf.imageCache[testfile]
    img2 = pyf.imageCache[benchmark]

    hdr1   = img1.header
    hdr2   = img2.header
    fields = ['dim',       'pixdim',     'intent_code',
              'datatype',  'qform_code', 'sform_code',
              'quatern_b', 'quatern_c',  'quatern_d',
              'qoffset_x', 'qoffset_y',  'qoffset_z',
              'srow_x',    'srow_y',     'srow_z']

    for f in fields:
        f1 = hdr1[f]
        f2 = hdr2[f]

        if (not alldims) and (f in ('dim', 'pixdim')):
            ndim = img1.header['dim'][0]
            f1   = f1[:ndim + 1]
            f2   = f2[:ndim + 1]

        if not np.all(np.isclose(f1, f2)):
            return 1

    return 0


def evalHeaderRestrictDims(pyf, testfile, benchmark):
    """Evaluation routine which compares the header fields of two NIFTI
    images. For the `dim` and `pixdim` fields, only the entries which
    are expected to be valid (e.g. `dim1`, `dim2`, and `dim3` for a 3D image)
    are compared.

    Returns 0 if they all match, 1 otherwise.
    """
    return evalHeader(pyf, testfile, benchmark, alldims=False)


def evalImage(pyf, testfile, benchmark):
    """Evaluation routine which compares the data from two NIFTI images.

    The :func:`cmpArrays` function does the calculation.
    """

    img1  = pyf.imageCache[testfile]
    img2  = pyf.imageCache[benchmark]
    data1 = img1.get_data()
    data2 = img2.get_data()

    return cmpArrays(data1, data2)


def evalNumericalText(pyf, testfile, benchmark):
    """Evaluation routine which compares the numerical data from two text
    files.

    The :func:`cmpArrays` function does the calculation.
    """

    data1 = common.loadNumericText(testfile)
    data2 = common.loadNumericText(benchmark)

    return cmpArrays(data1, data2)


def evalMD5(pyf, testfile, benchmark):
    """Compares the given files by calculating their MD5 hash. Returns
    0 if the hashes match, 1 otherwise.
    """

    hash1 = hashing.hashFile(testfile)
    hash2 = hashing.hashFile(benchmark)

    if hash1 != hash2: return 1
    else:              return 0


def evalVectorImage(pyf, testfile, benchmark):
    """Compares the given NIFTI images. It is assumed that they are
    both vector images, where each voxel contains a 3-dimensional
    vector, undirected, and centered at 0.
    """
    pion2 = np.pi / 2
    img1  = pyf.imageCache[testfile]
    img2  = pyf.imageCache[benchmark]

    data1 = img1.get_data().reshape(-1, 3).T
    data2 = img2.get_data().reshape(-1, 3).T

    # Calculate the length of each vector,
    # discard vectors of length 0, and
    # normalise each vector to unit length
    len1  = np.linalg.norm(data1, axis=0)
    len2  = np.linalg.norm(data2, axis=0)
    nz1   = len1 > 1e-6
    nz2   = len2 > 1e-6
    nz    = nz1 & nz2

    data1 = data1[:, nz] / len1[nz]
    data2 = data2[:, nz] / len2[nz]
    len1  = len1[nz]
    len2  = len2[nz]

    # Calculate the angle between each vector.
    # Vectors are undirected, and centered at
    # (0, 0, 0), so the maximum possible angle
    # we can have is 90 degrees.
    dot          = np.sum(data1 * data2, axis=0)
    dot          = np.clip(dot, -1, 1)
    angle        = np.arccos(dot)
    amask        = angle > pion2
    angle[amask] = np.pi - angle[amask]

    # We also compare the length of each
    # vector, and the pattern of missing
    # voxels (vectors of length 0)
    nzcorr  = np.abs(np.corrcoef(nz1, nz2)[0, 1])
    lendiff = np.abs(len1 - len2) / np.max((len1, len2), axis=0)
    angle   = np.abs(angle) / pion2

    if np.isnan(nzcorr):
        nzcorr = 1

    # All errors are normalised to
    # the range (0, 1). We return
    # the worst error
    nzError    = 1 - nzcorr
    angleError = angle.mean()
    lenError   = lendiff.mean()

    return max((nzError, lenError, angleError))


def evalPolarCoordinateImageGroup(pyf, testfiles, benchmarks):
    """Compares the values in a set of files containing 3D polar coordinates.

    Currently only the ``phi`` and ``theta`` outputs of ``bedpostx`` are
    understood.

    The coordinates are converted into vectors, and then passed to the
    :func:`evalVectorImage` function.
    """

    thetapatterns = [
        'mean_th?samples.*',
        'merged_th?samples.*',
    ]

    phipatterns = [
        'mean_ph?samples.*',
        'merged_ph?samples.*',
    ]

    def matches(fname, patterns):
        return any([fnmatch.fnmatch(op.basename(fname), p) for p in patterns])

    testtheta  = [f for f in testfiles  if matches(f, thetapatterns)]
    testphi    = [f for f in testfiles  if matches(f, phipatterns)]
    benchtheta = [f for f in benchmarks if matches(f, thetapatterns)]
    benchphi   = [f for f in benchmarks if matches(f, phipatterns)]

    if any((len(testfiles)  != 2,
            len(benchmarks) != 2,
            len(testtheta)  != 1,
            len(testphi)    != 1,
            len(benchtheta) != 1,
            len(benchphi)   != 1)):
        raise ValueError('Wrong number of files: {} <-> {}'
                         ''.format(testfiles, benchmarks))

    testtheta  = pyf.imageCache[testtheta[ 0]].get_data()
    testphi    = pyf.imageCache[testphi[   0]].get_data()
    benchtheta = pyf.imageCache[benchtheta[0]].get_data()
    benchphi   = pyf.imageCache[benchphi[  0]].get_data()

    if any((testphi   .shape != testtheta.shape,
            benchtheta.shape != testtheta.shape,
            benchphi  .shape != testtheta.shape)):
        raise ValueError('Image shapes don\'t match')

    testvec  = np.zeros(tuple(testtheta.shape) + (3,))
    benchvec = np.zeros(tuple(testtheta.shape) + (3,))

    testvec[ ..., 0] = np.sin(testtheta)  * np.cos(testphi)
    testvec[ ..., 1] = np.sin(testtheta)  * np.sin(testphi)
    testvec[ ..., 2] = np.cos(testtheta)
    benchvec[..., 0] = np.sin(benchtheta) * np.cos(benchphi)
    benchvec[..., 1] = np.sin(benchtheta) * np.sin(benchphi)
    benchvec[..., 2] = np.cos(benchtheta)

    testvec  = nib.Nifti1Image(testvec,  np.eye(4), None)
    benchvec = nib.Nifti1Image(benchvec, np.eye(4), None)

    name = 'evalPolarCoordinateImageGroup_' + '_'.join(testfiles)

    pyf.imageCache[name + '_test']      = testvec
    pyf.imageCache[name + '_benchmark'] = benchvec

    return evalVectorImage(pyf, name + '_test', name + '_benchmark')


def evalGiftiVertices(pyf, testfile, benchmark):
    """Compare the vertices of two GIFTI surfaces. Uses the :func:`cmpArrays`
    function.
    """

    surf1 = pyf.imageCache[testfile]
    surf2 = pyf.imageCache[benchmark]

    # NIFTI_INTENT_POINTSET == 1008
    verts1 = [d for d in surf1.darrays if d.intent == 1008][0].data
    verts2 = [d for d in surf2.darrays if d.intent == 1008][0].data

    return cmpArrays(verts1, verts2)


def cmpArrays(arr1, arr2):
    """Compares the values in the given ``numpy`` arrays.

    Returns the mean difference between the two arrays, normalised
    by the combined data range of the two arrays.
    """

    arr1 = np.asarray(arr1, dtype=np.float128)
    arr2 = np.asarray(arr2, dtype=np.float128)

    # Non-finite values (nan/inf)
    # must match in both arrays.
    finite = np.isfinite(arr1)

    if not np.all(finite == np.isfinite(arr2)):
        return 1

    # only consider voxels where
    # we have at least one non-zero
    # value
    nzmask = finite & ((arr1 != 0) | (arr2 != 0))

    # all infinite or
    # all zero - all good
    if ~np.any(nzmask):
        return 0

    arr1 = arr1[nzmask]
    arr2 = arr2[nzmask]

    # Calculate the difference between the two
    # arrays, and scale it by the combined data
    # range of the two arrays, so that all of
    # the errors are proportional to the range
    # of the data.
    denom = np.max((arr1, arr2)) - np.min((arr1, arr2))

    # if the above results in 0, it
    # means that all voxels from both
    # arrays have the same value
    if denom == 0:
        return 0

    normdiff = np.abs((arr2 - arr1) / denom)

    # The final error is the mean error across all voxels
    return normdiff.mean()
