#!/usr/bin/env python
#
# hashing.py - Pyfeeds test verification
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains functions used by pyfeeds to perform **test
verificiation** - identifying when a test or its data has changed since it was
last executed.


Pyfeeds implements a simple change-tracking mechanism so it can warn the user
when the contents of a test directory, or the external data dependencies of
a test have changed. The following functions are provided to use this
mechanism:

 .. autosummary::
    :nosignatures:

    genHashes
    checkHashes
    calcHashes
    loadHashes
    saveHashes
    checkTestHash
    hashPath
    hashFile
"""


from __future__ import print_function
from __future__ import division

import            os
import os.path as op
import            logging
import            hashlib


from . import common


log = logging.getLogger(__name__)


def genHashes(pyf):
    """Generates verification hashes for all of the given tests, and
    prints them to standard output, or writes them to a file.

    :arg pyf: A :class:`.Pyfeeds` instance.
    """

    tests    = pyf.tests
    inputDir = pyf.inputDir

    testHashes  = []
    inputHashes = []

    log.info('Calculating test hashes ...')

    testHashes, inputHashes = calcHashes(tests, inputDir)

    # Hashes can be None, so make
    # sure they're formatted as strings
    testHashes  = [str(h) for h in testHashes]
    inputHashes = [str(h) for h in inputHashes]

    # Write hashes to hashFile
    if pyf.hashFileProvided:

        log.info('Saving test hashes to {} ...'.format(pyf.hashFile))

        hashes = {th : ih for th, ih in zip(testHashes, inputHashes)}
        saveHashes(pyf.hashFile, hashes)

    # Otherwise, print hashes to standard output
    else:
        testNames  = [t.name for t in tests]
        titles     = ['Test name', 'Test directory hash', 'Test data hash']

        print('\nTest verification hashes\n')
        common.printColumns(titles, [testNames, testHashes, inputHashes])


def checkHashes(pyf):
    """Calculates verification hashes for all of the given tests, compares
    them against the saved hashes, then prints a summary to standard output
    outlining which tests have changed.

    :arg pyf: A :class:`.Pyfeeds` instance.
    """

    tests    = pyf.tests
    inputDir = pyf.inputDir
    force    = pyf.forceHashes
    hashFile = pyf.hashFile

    if hashFile is not None:
        hashFile = op.abspath(hashFile)
    savedHashes = loadHashes(hashFile)

    results = [checkTestHash(pyf, t, inputDir, savedHashes, False, force)
               for t in tests]
    results = [TEST_HASH_STRINGS[r] for r in results]
    names   = [t.name for t in tests]

    titles = ['Test name', 'Verification test result']

    print('\nTest verification results\n')
    common.printColumns(titles, [names, results])


def calcHashes(tests, inputDir):
    """Calculates verification hashes for all of the given tests. A tuple
    containing the following is returned:

      - A list of the test directory hashes
      - A list of the test input hashes

    :arg tests:    A list of :class:`.Test` object.
    :arg inputDir: Directory in which the shared data is located.
    """

    if inputDir is not None:
        inputDir = op.abspath(inputDir)

    testHashes  = []
    inputHashes = []

    for test in tests:

        log.debug('Calculating hashes for test {} ...'.format(test.name))

        testHashes.append(test.hashTestDir())

        if inputDir is None: inputHashes.append(None)
        else:                inputHashes.append(test.hashInputs(inputDir))

    return testHashes, inputHashes


def loadHashes(hashFile):
    """Loads verification hashes from the given file. The hashes are returned
    as a dictionary of ``{testHash : dataHash}`` mappings.

    :arg hashFile: File to load the hashes from (e.g. ``.feedsHashes``).
    """

    if hashFile is None or not op.exists(hashFile):
        return {}

    log.debug('Loading test data hashes from {}'.format(hashFile))

    hashes = {}

    with open(hashFile, 'rt') as f:

        for i, line in enumerate(f):

            if line.strip() == '':
                continue

            try:
                testHash, inputHash = line.split()

                # 'None' in the hash file indicates
                # that the test does not have any
                # shared data
                if inputHash == 'None':
                    inputHash = None

            except Exception:
                log.warning('Malformed line in {} [{}]: {}'.format(
                    hashFile, i, line))
                continue

            hashes[testHash]  = inputHash

    return hashes


def saveHashes(hashFile, hashes):
    """Saves the given verification hashes to the specified file.

    :arg hashFile: File to save the hashes to (e.g. ``.feedsHashes``).

    :arg hashes:   A dictionary of verification hashes, in the same format
                   as that returned by the :func:`loadHashes` function.
    """

    log.debug('Saving test data hashes to {}'.format(hashFile))

    lines = ['{} {}'.format(th, ih) for th, ih in hashes.items()]

    with open(hashFile, 'wt') as f:

        f.write('\n'.join(lines) + '\n')


TEST_HASH_NO_INPUTS = 0
"""Return code for the :func:`checkTestHash` function. This code indicates
that the test hash was valid, and that the test does not have any external
data dependencies, hence has no data hash.
"""


TEST_HASH_PASSED = 1
"""Return code for the :func:`checkTestHash` function. This code indicates
that both the test hash and the data hash were valid.
"""


TEST_HASH_SKIPPED_NOCHANGE = 2
"""Return code for the :func:`checkTestHash` function. This code indicates
that the test verification was skipped , as the test input data had not been
modified since the last time the hashes were generated.
"""


TEST_HASH_FAILED_TEST_HASH = 3
"""Return code for the :func:`checkTestHash` function. This code indicates
that the test hash could not be found in the dictionary, either because
this is a new test, or because the contents of the test directory have
changed.
"""


TEST_HASH_FAILED_DATA_HASH = 4
"""Return code for the :func:`checkTestHash` function. This code indicates
that the calculated data hash does not match the stored hash, meaning
that the data for this test has changed since the hashes were last calculated.
"""


TEST_HASH_NOT_CHECKED = -1
"""This is a dummy code, used by the :func:`runTests` function to indicate
that the data integrity check has been skipped.
"""


TEST_HASH_STRINGS = {
    TEST_HASH_NOT_CHECKED       : 'Not checked',
    TEST_HASH_PASSED            : 'Passed',
    TEST_HASH_SKIPPED_NOCHANGE  : 'Skipped (data not changed since last '
                                  'check)',
    TEST_HASH_NO_INPUTS         : 'Passed (test does not use any shared data)',
    TEST_HASH_FAILED_TEST_HASH  : 'Failed (test directory changed, or this is '
                                  'a new test)',
    TEST_HASH_FAILED_DATA_HASH  : 'Failed (shared test data changed)',
}
"""Human-readable descriptions for each of the test hash results. """


TEST_HASH_SHORT_STRINGS = {
    TEST_HASH_NOT_CHECKED       : 'Not checked',
    TEST_HASH_PASSED            : 'Passed',
    TEST_HASH_SKIPPED_NOCHANGE  : 'Skipped (no change)',
    TEST_HASH_NO_INPUTS         : 'No data',
    TEST_HASH_FAILED_TEST_HASH  : 'New test, or test has changed',
    TEST_HASH_FAILED_DATA_HASH  : 'Data has changed',
}
"""Shorter human-readable descriptions for the test hash results. """


def checkTestHash(pyf,
                  test,
                  inputDir,
                  testHashes,
                  updateHashes,
                  forceCheck=False):
    """Calculates verification hashes for the given :class:`.Test`, and compares
    them against the hashes stored in the ``testHashes`` dictionary.  One of
    the following codes is returned, indicating the outcome of the
    verification check:

    .. autosummary::

       TEST_HASH_NO_INPUTS
       TEST_HASH_PASSED
       TEST_HASH_SKIPPED_NOCHANGE
       TEST_HASH_FAILED_TEST_HASH
       TEST_HASH_FAILED_DATA_HASH

    :arg pyf:         The :class:`.Pyfeeds` instance.

    :arg test:         The :class:`.Test` object to check.

    :arg inputDir:     Directory in which the shared data is located.

    :arg testHashes:   Dictionary of stored test hashes, in the format returned
                       by the :func:`loadHashes` function.

    :arg updateHashes: If ``True``, and the verification fails, the
                       ``testHashes`` dictionary is updated with the newly
                       calculated test/data hash values.

    :arg forceCheck:   If ``True``, the check is always performed, even if the
                       test data file timestamps indicate that they have not
                       not changed.
    """

    log.debug('Verifying input data for test {}'.format(test))

    # Generate hashes for the test directory, and
    # retrieve the stored input data hash from the
    # testHashes dictionary. If the testHash is
    # not in the dictionary, oldInputHash will be
    # a reference to the test object. We do this
    # because 'None' is a valid value for a data
    # hash.
    testHash     = test.hashTestDir()
    oldInputHash = testHashes.get(testHash, test)

    # If a hash has previously been calculated
    # on this test, check to see if the test
    # inputs have changed at all since the last
    # hash calculation time. If they haven't
    # we're going to skip the input hash
    # calculation.
    if (inputDir is not None) and \
       (not forceCheck)       and \
       (oldInputHash is not test):
        if not test.inputsChangedSince(inputDir, pyf.hashesLastGenerated):
            log.debug('Test %s data has not changed since '
                      'the last hash calculation - skipping.', test)
            return TEST_HASH_SKIPPED_NOCHANGE

    # Generate hashes for the test data
    if inputDir is not None:
        newInputHash = test.hashInputs(inputDir)
    else:
        newInputHash = None

    log.debug('Test {} input check: testHash={}, '
              'oldInputHash={}, newInputHash={}'.format(
                  test.name, testHash, newInputHash, oldInputHash))

    # This test has no inputs, and hence no hash
    if (newInputHash is None) and (oldInputHash is None):
        return TEST_HASH_NO_INPUTS

    # The hashes match
    if newInputHash == oldInputHash:
        return TEST_HASH_PASSED

    # The test directory hash could not
    # be found in the testHashes dict
    result = None
    if oldInputHash is test:

        result = TEST_HASH_FAILED_TEST_HASH

        log.warning('Test {} hashes not found in dictionary! This either '
                    'means that this is a new test which has not previously '
                    'been verified (in which case this warning can be '
                    'ignored), or that the contents of the test directory has '
                    'changed since it was last verified.'.format(test.name))

    # The test input data
    # hashes do not match
    else:
        result = TEST_HASH_FAILED_DATA_HASH

        log.warning('Test {} data verification failed! It looks like the '
                    'shared data used by this test has changed since the '
                    'test was last run.'.format(test.name))

    if updateHashes:
        log.debug('The updateHashes flag is set - adding/overwriting '
                  'the hash values for test {}.'.format(test.name))
        testHashes[testHash] = newInputHash

    return result


def hashPath(path, hashObj):
    """Recursively calculates MD5 digests of every file found from the
    given starting point. If ``path`` is a file, the ``hashObj`` is
    updated with the hex digest of its contents - a hash of hashes (see
    the :func:`hashFile` function). Otherwise, if ``path`` is a directory,
    this method is recursively called with its children.

    :arg path:    A file or directory path.

    :arg hashObj: A ``hashlib.md5`` object.

    :returns:     The number of files which were hashed.
    """

    if op.isfile(path):
        count = 1
        hashObj.update(hashFile(path).encode('ascii'))

    elif op.isdir(path):

        # listdir does not guarantee a specific
        # ordering, so we sort the result to
        # ensure a consistent hash value
        count = 0
        for p in sorted(os.listdir(path)):

            p      = op.join(path, p)
            count += hashPath(p, hashObj)

    else:

        count = 0
        log.warning('Attempt to hash invalid path: "{}"'.format(path))

    return count



hashCache = {}
"""This dictionary is used by the :meth:`hashFile` method. Whenever a md5
digest is calculated on a file, it is stored in this dictionary. Before a
file is hashed, this cache is checked, and the cached value (if present)
is used instead of re-calculating the hash. The dictionary structure is
``{ filePath : hexdigest }``.
"""


def hashFile(path):
    """Calculates an MD5 digest of the given file path.

    :arg path: Path to a file to be hashed.

    :returns:  A string containing the hexadecimal digest.
    """

    cached = hashCache.get(path)

    if cached is not None:
        log.debug('Using cached md5 digest for {}'.format(path))
        return cached

    hashObj = hashlib.md5()

    log.debug('Calculating md5 digest for {}'.format(path))

    with open(path, 'rb') as f:
        hashObj.update(f.read())

    digest          = hashObj.hexdigest()
    hashCache[path] = digest

    return digest
