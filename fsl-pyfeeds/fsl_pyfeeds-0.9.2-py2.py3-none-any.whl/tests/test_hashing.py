#!/usr/bin/env python
#
# test_hashing.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


from collections import OrderedDict
import textwrap as tw
import datetime
import os.path as op
import time

from pyfeeds import hashing, testing

from . import CaptureStdout, makepyfeeds, maketest, makepaths, tempdir


def test_genHashes():

    with tempdir():
        maketest('test1/feedsRun', inputs=['test1/file1', 'test1/file2'])
        maketest('test2/feedsRun', inputs=['test2/file1', 'test2/file2'])
        makepaths(['data/test1/file1',
                   'data/test1/file2',
                   'data/test2/file1',
                   'data/test2/file2'])

        pyf = makepyfeeds(command='genhash',
                          testDir=['.'],
                          inputDir='data',
                          hashFile='hashes')
        hashing.genHashes(pyf)
        assert op.exists('hashes')

        cap = CaptureStdout()
        with cap:
            pyf = makepyfeeds(command='genhash',
                              testDir=['.'],
                              inputDir='data')
            hashing.genHashes(pyf)
            test1, test2 = pyf.tests
        print(cap.stdout)
        lines = cap.stdout.strip().split('\n')

        assert 'test1' in lines[4]                    and \
                test1.hashTestDir()       in lines[4] and \
                test1.hashInputs('data')  in lines[4]
        assert 'test2' in lines[5]                    and \
                test2.hashTestDir()       in lines[5] and \
                test2.hashInputs('data')  in lines[5]



def test_checkHashes():
    cap = CaptureStdout()
    with tempdir(), cap:
        maketest('test1/feedsRun', inputs=['test1/file1', 'test1/file2'])
        maketest('test2/feedsRun', inputs=['test2/file1', 'test2/file2'])
        makepaths(['data/test1/file1',
                   'data/test1/file2',
                   'data/test2/file1',
                   'data/test2/file2'])

        pyf = makepyfeeds(command='checkhash',
                          testDir=['.'],
                          inputDir='data')

        hashing.checkHashes(pyf)


def test_calcHashes():
    with tempdir():
        maketest('test1/feedsRun', inputs=['data/test1/file1', 'data/test1/file2'])
        maketest('test2/feedsRun', inputs=['data/test2/file1', 'data/test2/file2'])
        makepaths(['data/test1/file1',
                   'data/test1/file2',
                   'data/test2/file1',
                   'data/test2/file2'])

        test1 = testing.Test('test1/feedsRun', '.')
        test2 = testing.Test('test2/feedsRun', '.')

        testHashes, inputHashes = hashing.calcHashes([test1, test2], 'data')

        assert testHashes  == [test1.hashTestDir(),
                               test2.hashTestDir()]
        assert inputHashes == [test1.hashInputs('data'),
                               test2.hashInputs('data')]

        testHashes, inputHashes = hashing.calcHashes([test1, test2], None)
        assert testHashes  == [test1.hashTestDir(),
                               test2.hashTestDir()]
        assert inputHashes == [None, None]



def test_loadHashes():
    contents = tw.dedent("""
    123 456
    abc def

    987 654
    badline
    111 None
    """).strip()
    with tempdir():
        with open('hashfile', 'wt') as f:
            f.write(contents)

        hashes = hashing.loadHashes('hashfile')
        assert hashes == {'123' : '456',
                          'abc' : 'def',
                          '987' : '654',
                          '111' : None}


def test_saveHashes():
    contents = tw.dedent("""
    123 456
    abc def
    987 654
    111 None
    """).strip()

    hashes = OrderedDict([('123', '456'),
                          ('abc', 'def'),
                          ('987', '654'),
                          ('111', None)])

    with tempdir():

        hashing.saveHashes('hashfile', hashes)
        with open('hashfile', 'rt') as f:
            assert f.read().strip() == contents

    pass


def test_checkTestHash():
    before = datetime.datetime.now()
    time.sleep(1)
    with tempdir():
        maketest('test1/feedsRun', inputs=['test1/file1', 'test1/file2'])
        makepaths(['data/test1/file1',
                   'data/test1/file2'])

        after = datetime.datetime.now()

        pyf = makepyfeeds(command='checkhash',
                          testDir=['.'],
                          inputDir='data')
        pyf.hashesLastGenerated = before
        test = pyf.tests[0]

        hashes = { test.hashTestDir() : test.hashInputs('data') }

        assert hashing.checkTestHash(pyf, test, 'data', hashes, False, False) == hashing.TEST_HASH_PASSED

        pyf.hashesLastGenerated = after
        assert hashing.checkTestHash(pyf, test, 'data', hashes, False, False) == hashing.TEST_HASH_SKIPPED_NOCHANGE

        pyf.hashesLastGenerated = before
        hashes = { test.hashTestDir() : 'poop' }
        assert hashing.checkTestHash(pyf, test, 'data', hashes, False, False) == hashing.TEST_HASH_FAILED_DATA_HASH

        assert hashing.checkTestHash(pyf, test, 'data', {}, False, False) == hashing.TEST_HASH_FAILED_TEST_HASH
