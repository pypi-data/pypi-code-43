#!/usr/bin/env python
#
# test_testing.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import os
import datetime
import os.path as op

from . import tempdir, makepaths, maketest, makepyfeeds, CaptureStdout

from  pyfeeds import testing


def test_findTestDirs():
    with tempdir():
        makepaths(('test1/feedsRun',
                   'test2/feedsRun',
                   'test3/a/feedsRun',
                   'test3/b/feedsRun',
                   'test4/feedsRun',
                   'test4/feedsRun.a',
                   'test4/feedsRun.b'))
        got = list(sorted(testing.findTestDirs(os.getcwd())))
        exp = ['test1',
               'test2',
               'test3/a',
               'test3/b',
               'test4']

        got = [op.abspath(p) for p in got]
        exp = [op.abspath(p) for p in exp]

        assert got == exp


def test_findTestScripts():
    def check(got, exp):
        got = list(sorted([op.abspath(p) for p in got]))
        exp = list(sorted([op.abspath(p) for p in exp]))
        assert got == exp

    tests = [
        ['./feedsRun'],
        ['./feedsRun.a', './feedsRun..b'],
        ['./feedsRun', './feedsRun.a', './feedsRun.b']]


    for paths in tests:
        with tempdir():
            makepaths(paths)
            got = testing.findTestScripts('.')
            check(got, paths)

    with tempdir():
        makepaths(['feedsRu', 'feedsRun.', '.feedsRun'])
        assert testing.findTestScripts('.') == []



def test_listTests():
    cap = CaptureStdout()
    with tempdir(), cap:

        tests = ['test1/feedsRun',
                 'test2/feedsRun',
                 'test3/subdir1/feedsRun',
                 'test3/subdir2/feedsRun',
                 'test4/feedsRun',
                 'test4/feedsRun.abc',
                 'test4/feedsRun.def']

        makepaths(tests)

        pyf = makepyfeeds(command='list', testDir=['.'])
        testing.listTests(pyf)

        tkns = cap.stdout.split()

        for test in tests:
            dirname = op.dirname(test)
            assert dirname             in tkns
            assert op.abspath(dirname) in tkns



def test_Test():
    with tempdir():
        maketest('test1/feedsRun', inputs=['data/file1', 'data/file2'])

        test = testing.Test('test1/feedsRun', '.')

        assert test.name  == 'test1'
        assert str(test)  == 'test1'
        assert repr(test) == 'test1'
        assert test.getInputs() == ['data/file1', 'data/file2']

        makepaths(['inputData/data/file1', 'inputData/data/file2'])
        test.inputsChangedSince('inputData', datetime.datetime.now())
        test.hashTestDir()
        test.hashInputs('inputData')
        os.mkdir('sandbox')
        test.createSandbox('inputData', 'sandbox')

        maketest('test1/subdir/feedsRun')
        test = testing.Test('test1/subdir/feedsRun', '.')
        assert test.name == 'test1/subdir'

        maketest('test1/subdir/feedsRun')
        maketest('test1/subdir/feedsRun.abc')
        maketest('test1/subdir/feedsRun.def')
        test = testing.Test('test1/subdir/feedsRun', '.')
        assert test.name == 'test1/subdir'
        test = testing.Test('test1/subdir/feedsRun.abc', '.')
        assert test.name == 'test1/subdir/abc'
        test = testing.Test('test1/subdir/feedsRun.def', '.')
        assert test.name == 'test1/subdir/def'


def test_bundleTests():
    with tempdir():
        maketest(  'tests/test1/feedsRun',
                   inputs=['data/file1', 'data/file2'])
        makepaths(['tests/test1/datafile',
                   'inputData/data/file1',
                   'inputData/data/file2',
                   'benchmarkData/test1/outfile1',
                   'benchmarkData/test1/outfile2'])

        pyf = makepyfeeds(command='bundle',
                          testDir=['tests'],
                          inputDir='inputData',
                          benchmarkDir='benchmarkData',
                          outputDir='bundleDir',
                          genHashes=True,
                          overwrite=True)

        testing.bundleTests(pyf)

        assert op.exists('bundleDir/tests/test1/feedsRun')
        assert op.exists('bundleDir/tests/test1/datafile')
        assert op.exists('bundleDir/data/.feedsHashes')
        assert op.exists('bundleDir/data/data/file1')
        assert op.exists('bundleDir/data/data/file2')
        assert op.exists('bundleDir/benchmarks/test1/outfile1')
        assert op.exists('bundleDir/benchmarks/test1/outfile2')

        pyf = makepyfeeds(command='bundle',
                          testDir=['tests'],
                          benchmarkDir='benchmarkData',
                          outputDir='bundleDir',
                          overwrite=True)
        testing.bundleTests(pyf)
        assert     op.exists('bundleDir/tests/test1/feedsRun')
        assert     op.exists('bundleDir/tests/test1/datafile')
        assert not op.exists('bundleDir/data')
        assert     op.exists('bundleDir/benchmarks/test1/outfile1')
        assert     op.exists('bundleDir/benchmarks/test1/outfile2')

        pyf = makepyfeeds(command='bundle',
                          testDir=['tests'],
                          outputDir='bundleDir',
                          overwrite=True)
        testing.bundleTests(pyf)
        assert     op.exists('bundleDir/tests/test1/feedsRun')
        assert     op.exists('bundleDir/tests/test1/datafile')
        assert not op.exists('bundleDir/data')
        assert not op.exists('bundleDir/benchmarks')


def test_runTest():
    with tempdir():
        maketest('tests/test1/feedsRun', returnCode=0, stdout=['output1', 'output2'])
        maketest('tests/test2/feedsRun', returnCode=1)
        os.mkdir('output/')
        os.chmod('tests/test1/feedsRun', 0o755)
        os.chmod('tests/test2/feedsRun', 0o755)

        pyf = makepyfeeds(command='run',
                          testDir=['tests'],
                          outputDir='output',
                          overwrite=True)

        gott1 = testing.runTest(pyf,
                                pyf.tests[0],
                                'output',
                                None,
                                None,
                                os.environ.copy(),
                                False)
        gott2 = testing.runTest(pyf,
                                pyf.tests[1],
                                'output',
                                None,
                                None,
                                os.environ.copy(),
                                False)

        assert     gott1[0]
        assert not gott2[0]

        with open('output/test1/feedsRun.log') as f:
            assert f.read().strip() == 'output1\noutput2'


def test_runTests():
    cap = CaptureStdout()
    with tempdir(), cap:
        maketest('tests/test1/feedsRun', returnCode=0, stdout=['output1', 'output2'])
        maketest('tests/test2/feedsRun', returnCode=1)
        os.mkdir('output/')
        os.chmod('tests/test1/feedsRun', 0o755)
        os.chmod('tests/test2/feedsRun', 0o755)

        pyf = makepyfeeds(command='run',
                          testDir=['tests'],
                          outputDir='output',
                          overwrite=True)

        testing.runTests(pyf)

    lines = cap.stdout.split('\n')
    assert 'test1' in lines[2] and 'Passed' in lines[2]
    assert 'test2' in lines[3] and 'Failed' in lines[3]
