###############################################################################
# (c) Copyright 2013 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import json
import tempfile
import os
import re
import shutil
import nose
from subprocess import Popen, PIPE, check_output
from xml.etree import ElementTree as ET
from os.path import normpath, join, exists, islink, isdir
from LbNightlyTools.tests.utils import *

_testdata = normpath(join(*([__file__] + [os.pardir] * 4 + ['testdata'])))

# Uncomment to disable the tests.
#__test__ = False

from LbNightlyTools.Scripts import Checkout
from LbNightlyTools import Utils
from LbNightlyTools import CheckoutMethods
from LbNightlyTools import Configuration

os.environ['LANG'] = 'C'

def test_retry_call():
    'Utils.retry_call()'
    # standard calls
    assert Utils.retry_call(['true']) == 0
    assert Utils.retry_call(['false']) == 1
    # calls with retry
    assert Utils.retry_call(['true'], retry=3) == 0
    try:
        Utils.retry_call(['false'], retry=3)
    except RuntimeError, x:
        assert str(x) == "the command ['false'] failed 3 times"


def get_git_branch(path):
    '''
    Return the branch currently checked out in a git repository.

    @param path: the path to a directory inside a git repository
    '''
    p = Popen(['git', 'branch'], stdout=PIPE, cwd=path)
    branches = p.communicate()[0].splitlines()
    for branch in branches:
        if branch.startswith('* '):
            branch = branch.split()[1]
            if not branch.startswith('('):  # marker for detached HEAD
                return branch
    return None  # no branch (detached HEAD)


def assert_git_branch(path, branch):
    local_branch = get_git_branch(path)
    assert local_branch == branch, 'local branch should be %s, %s found' % (branch, local_branch)

def check(files):
    '''
    Assert that all the given files exist.
    '''
    for f in files:
        assert exists(f), 'Missing %s' % f


def test_Project():
    'Configuration.Project'
    Project = Configuration.Project

    mockCheckout = MockFunc()

    p = Project('Gaudi', 'v23r5')
    assert p.name == 'Gaudi'
    assert p.version == 'v23r5'
    assert p.overrides == {}
    assert p._checkout == CheckoutMethods.default
    assert p.baseDir == 'Gaudi/'
    assert str(p) == 'Gaudi/v23r5'

    p = Project('LbScripts', 'HEAD')
    assert p.name == 'LbScripts'
    assert p.version == 'HEAD'
    assert p.overrides == {}
    assert p._checkout == CheckoutMethods.lbscripts
    assert p.baseDir == 'LbScripts/'
    assert str(p) == 'LbScripts/HEAD'

    p = Project('LHCb', 'v38r5')
    assert p.name == 'LHCb'
    assert p.version == 'v38r5'
    assert p.overrides == {}
    assert p._checkout == CheckoutMethods.default
    assert p.baseDir == 'LHCb/'
    assert str(p) == 'LHCb/v38r5'

    p = Project('Gaudi', 'head')
    assert p.name == 'Gaudi'
    assert p.version == 'HEAD'
    assert p.overrides == {}
    assert p._checkout == CheckoutMethods.default
    assert p.baseDir == 'Gaudi/'
    assert str(p) == 'Gaudi/HEAD'

    p = Project('Gaudi', 'v23r5', checkout=mockCheckout)
    assert p.name == 'Gaudi'
    assert p.version == 'v23r5'
    assert p.overrides == {}
    assert p._checkout == mockCheckout

    p = Project('Gaudi', 'v23r5',
                overrides={'GaudiPolicy': 'head',
                           'GaudiProfiling': None,
                           'GaudiObjDesc': 'v11r17'},
                checkout=mockCheckout)
    assert p.name == 'Gaudi'
    assert p.version == 'v23r5'
    assert p.overrides == {'GaudiPolicy': 'head',
                           'GaudiProfiling': None,
                           'GaudiObjDesc': 'v11r17'}
    assert p._checkout == mockCheckout

    cb = MockFunc()
    p = Project('Gaudi', 'v23r5', checkout=cb)
    p.checkout()
    assert cb.args == (p,), cb.args
    assert cb.kwargs == {}, cb.kwargs
    assert hasattr(p, 'checkout_log')
    assert p.checkout_log

    # test setting checkout_opts via checkout descriptor
    cb = MockFunc()
    p = Project('Gaudi', 'v23r5', checkout=(cb, {'special': False}))
    p.checkout()
    assert cb.args == (p,), cb.args
    assert cb.kwargs == {'special': False}, cb.kwargs


def test_Slot():
    'Configuration.Slot'
    Slot = Configuration.Slot
    Project = Configuration.Project

    #s = Slot('dummy')
    #assert len(s.projects) == 0
    #assert s.name == 'dummy'

    s = Slot(name='lhcb-gaudi-head')
    assert len(s.projects) == 0
    assert s.name == 'lhcb-gaudi-head'

    cb = MockFunc()
    p = Project('Gaudi', 'v23r5', checkout=cb)
    s = Slot('dummy', [p])
    s.checkout()
    assert cb.args == (p,), cb.args
    assert cb.kwargs == {}, cb.kwargs

def test_PartialCheckout():
    'PartialCheckout'
    Slot = Configuration.Slot
    Project = Configuration.Project

    gcb = MockFunc()
    p1 = Project('Gaudi', 'v23r5', checkout=gcb)
    lcb = MockFunc()
    p2 = Project('LHCb', 'HEAD', checkout=lcb)

    s = Slot('dummy', [p1, p2])
    s.checkout(projects=set(['Gaudi']))

    assert gcb.args == (p1,), gcb.args
    assert gcb.kwargs == {}, gcb.kwargs
    assert lcb.args == None
    assert lcb.kwargs == None

def test_parseConfigFile():
    'Configuration.parse()'

    doCall = lambda data: processFileWithName(json.dumps(data), 'dummy.json', Configuration.parse)

    CheckoutMethods.special_test = MockFunc()

    s = doCall({'projects':[{"name": "Gaudi",
                             "version": "v23r5",
                             "checkout": "special_test"},
                            {"name": "LHCb",
                             "version": "v32r5",
                             "overrides": {"GaudiObjDesc": "HEAD",
                                           "GaudiPython": "v12r4",
                                           "Online/RootCnv": None}}]})
    assert s.name == 'dummy'
    assert len(s.projects) == 2
    p = s.projects[0]
    assert (p.name, p.version) == ('Gaudi', 'v23r5')
    assert p._checkout == CheckoutMethods.special_test #@UndefinedVariable
    p = s.projects[1]
    assert (p.name, p.version) == ('LHCb', 'v32r5')
    assert p._checkout == CheckoutMethods.default
    assert p.overrides == {"GaudiObjDesc": "HEAD",
                           "GaudiPython": "v12r4",
                           "Online/RootCnv": None}

    s = doCall({'projects':[], 'slot': 'lhcb-head'})
    assert s.name == 'lhcb-head'
    assert len(s.projects) == 0

    s = doCall({'projects':[{"name": "P",
                             "version": "V",
                             "checkout": "os.path.exists"}]})
    assert len(s.projects) == 1
    p = s.projects[0]
    assert (p.name, p.version) == ('P', 'V')
    assert p._checkout == os.path.exists

    try:
        s = doCall({'projects':[{"name": "Gaudi"}]})
    except (KeyError, TypeError):
        pass

def test_checkout():
    'checkout functions'
    if not which('getpack') or not which('git'):
        raise nose.SkipTest

    Project = Configuration.Project

    with TemporaryDir(chdir=True):
        # default method
        Project('Brunel', 'v44r1').checkout()
        check([join('Brunel', join(*x))
               for x in [('CMakeLists.txt',),
                         ('cmt', 'project.cmt'),
                         ('BrunelSys', 'cmt', 'requirements')]])
        shutil.rmtree('Brunel', ignore_errors=True)

        # default method
        Project('Brunel', 'head').checkout()
        check([join('Brunel', join(*x))
               for x in [('CMakeLists.txt',),
                         ('Rec', 'Brunel'),
                         ('BrunelSys',)]])
        shutil.rmtree('Brunel', ignore_errors=True)


        Project('Gaudi', 'v23r6',
                checkout=CheckoutMethods.git,
                checkout_opts=dict(url='https://gitlab.cern.ch/gaudi/Gaudi.git',
                                   commit='GAUDI/GAUDI_v23r6')).checkout()
        check([join('Gaudi', join(*x))
               for x in [('CMakeLists.txt',),
                         ('GaudiRelease',)]])
        assert_git_branch('Gaudi', None)
        shutil.rmtree('Gaudi', ignore_errors=True)

        Project('Gaudi', 'HEAD',
                checkout=CheckoutMethods.git).checkout(url='https://gitlab.cern.ch/gaudi/Gaudi.git')
        check([join('Gaudi', join(*x))
               for x in [('CMakeLists.txt',),
                         ('GaudiRelease',)]])

        shutil.rmtree('Gaudi', ignore_errors=True)

        Project('Gaudi', 'v23r6', checkout='git').checkout()
        check([join('Gaudi', join(*x))
               for x in [('CMakeLists.txt',),
                         ('GaudiRelease', )]])
        #assert 'v23r6' in open(join(tmpdir, 'GAUDI', 'GAUDI_v23r6', 'CMakeLists.txt')).read()
        assert_git_branch('Gaudi', None)
        shutil.rmtree('Gaudi', ignore_errors=True)


        Project('Gaudi', 'HEAD', checkout='git').checkout()
        check([join('Gaudi', join(*x))
               for x in [('CMakeLists.txt',),
                         ('GaudiRelease', )]])
        shutil.rmtree('Gaudi', ignore_errors=True)

        shutil.rmtree(join('Brunel'), ignore_errors=True)

        Project('Gaudi', 'HEAD',
                checkout=CheckoutMethods.git).checkout(url='https://gitlab.cern.ch/gaudi/Gaudi.git')
        check([join('Gaudi', join(*x))
               for x in [('CMakeLists.txt',),
                         ('GaudiRelease',)]])
        assert_git_branch('Gaudi', None)

        shutil.rmtree('Gaudi', ignore_errors=True)
        Project('Gaudi', 'v23r6', checkout='ignore').checkout()
        assert not exists('Gaudi')


def test_checkout_git_merge():
    'git checkout with merge'
    if not which('git'):
        raise nose.SkipTest

    Project = Configuration.Project

    with TemporaryDir(chdir=True):
        shutil.rmtree('Gaudi', ignore_errors=True)
        Project('Gaudi', 'mr150', checkout_opts={'commit': 'd7ecf7ef4~',
                                                 'merges': 150}).checkout()
        check([join('Gaudi', join(*x))
               for x in [('CMakeLists.txt',),
                         ('cmt', 'project.cmt'),
                         ('GaudiRelease', 'cmt', 'requirements')]])
        assert_git_branch('Gaudi', None)
        parents = check_output(['git', 'log', '-n', '1', '--format=%P'],
                               cwd='Gaudi').split()
        assert parents == ['d0ae829e30635db53f6335728120790ef453681f', '7538b5246b0e91442003057bbdcc7843e37ac58e']

        # FIXME: this test relies too much on conditions and the time of writing (not met anymore)
        # shutil.rmtree(join('GAUDI', 'GAUDI_HEAD'), ignore_errors=True)
        # Project('Gaudi', 'head',
        #         checkout_opts = {'merges': [147,
        #                                     ('https://gitlab.cern.ch/clemenci/Gaudi.git', 'remove-gccxml-dep', 'clemenci'),
        #                                     ('https://gitlab.cern.ch/clemenci/Gaudi.git', 'GAUDI-1048'),
        #                                     (None, '7538b524', 'clemenci'),
        #                                     ]}).checkout()
        # assert_git_branch(join('GAUDI', 'GAUDI_HEAD'), 'master')


def test_checkout_export():
    'checkout functions with option "export"'
    if not which('git'):
        raise nose.SkipTest

    Project = Configuration.Project

    with TemporaryDir(chdir=True):
        Project('Brunel', 'v44r1').checkout(export=True)
        check([join('Brunel', join(*x))
               for x in [('CMakeLists.txt',),
                         ('cmt', 'project.cmt'),
                         ('BrunelSys', 'cmt', 'requirements')]])
        assert not exists(join('Brunel', '.git'))

        Project('Gaudi', 'v23r6',
                checkout='git',
                checkout_opts={'url': 'https://gitlab.cern.ch/gaudi/Gaudi.git',
                               'export': True}).checkout()
        check([join('Gaudi', join(*x))
               for x in [('CMakeLists.txt',),
                         ('cmt', 'project.cmt'),
                         ('GaudiRelease', 'cmt', 'requirements')]])
        assert not exists(join('Gaudi', '.git'))

def test_dependencies():
    expected = {'LCGCMT': [],
                'Gaudi': ['LCGCMT'],
                'Online': ['Gaudi'],
                'LHCb': ['Gaudi'],
                'Lbcom': ['LHCb'],
                'Rec': ['LHCb'],
                'Brunel': ['Lbcom', 'Rec'],
                'NewProj': ['Brunel', 'Online']
                }

    mlh = MockLoggingHandler()
    import LbNightlyTools
    LbNightlyTools.Configuration.__log__.addHandler(mlh)

    rootdir = join(_testdata, 'collect_deps', 'cmt')
    slot = Configuration.parse(join(rootdir, 'conf.json'))
    with Utils.chdir(rootdir):
        deps = slot.dependencies()
    print 'CMT:', deps
    assert deps == expected
    assert len(mlh.messages['warning']) == 1
    assert 'LCGCMT' in mlh.messages['warning'].pop()

    rootdir = join(_testdata, 'collect_deps', 'cmake')
    slot = Configuration.parse(join(rootdir, 'conf.json'))
    with Utils.chdir(rootdir):
        deps = slot.dependencies()
    print 'CMake:', deps
    assert deps == expected
    assert len(mlh.messages['warning']) == 1
    assert 'LCGCMT' in mlh.messages['warning'].pop()

    rootdir = join(_testdata, 'collect_deps', 'broken')
    slot = Configuration.parse(join(rootdir, 'conf.json'))
    with Utils.chdir(rootdir):
        deps = slot.dependencies()
    expected = {'Gaudi': [],
                'BadCMT': [],
                'BadCMake': [],
                'Missing': []}
    print 'Broken:', deps
    assert deps == expected
    warnings = mlh.messages['warning']
    assert filter(re.compile(r'cannot discover dependencies for BadCMT').match, warnings)
    assert filter(re.compile(r'cannot discover dependencies for BadCMake').match, warnings)
    assert filter(re.compile(r'cannot discover dependencies for Missing').match, warnings)
    assert not filter(re.compile(r'cannot discover dependencies for Gaudi').match, warnings)

def test_checkout_datapkgs():
    '''checkout a single data package (getpack)'''
    if not which('getpack'):
        raise nose.SkipTest

    Package = Configuration.Package
    mlh = MockLoggingHandler()
    Checkout.__log__.addHandler(mlh)

    with TemporaryDir(chdir=True):
        pkg = Package(name='AppConfig', version='v3r198')
        pkg.checkout()
        assert exists(join('AppConfig', 'v3r198', 'cmt'))


    dbase = Configuration.DBASE([Package(name='AppConfig', version='v3r198')])
    param = Configuration.PARAM([Package(name='TMVAWeights', version='v1r1')])
    slot = Configuration.Slot('data-packs', projects=[dbase, param])

    with TemporaryDir(chdir=True):
        slot.checkout()

        assert exists(join('DBASE', 'AppConfig', 'v3r198', 'cmt'))
        assert exists(join('PARAM', 'TMVAWeights', 'v1r0', 'cmt'))

def test_checkout_datapkgs_old():
    '''checkout a single data package (getpack)'''
    if not which('getpack'):
        raise nose.SkipTest

    Package = Configuration.Package

    mlh = MockLoggingHandler()
    Checkout.__log__.addHandler(mlh)

    with TemporaryDir(chdir=True):
        os.makedirs('build')
        pkg = Package(name='AppConfig', version='v3r198')
        pkg.checkout()

        assert exists(join('AppConfig', 'v3r198', 'cmt'))

    slot = Configuration.parse(join(_testdata, 'data-packs.json'))
    with TemporaryDir(chdir=True):
        with Utils.chdir('build', create=True):
            slot.checkout()

        assert exists(join('build', 'DBASE', 'AppConfig', 'v3r198', 'cmt'))
        assert exists(join('build', 'PARAM', 'TMVAWeights', 'v1r0', 'cmt'))

def test_stack_checkout_datapkg():
    '''checkout a data package within a slot'''
    if not which('getpack'):
        raise nose.SkipTest

    Package = Configuration.Package

    mlh = MockLoggingHandler()
    Checkout.__log__.addHandler(mlh)

    with TemporaryDir(chdir=True):
        os.makedirs('build')
        pkgs = [Package(name='AppConfig', version='v3r198'),
                Package(name='Det/SQLDDDB', version='HEAD')]

        slot = Configuration.Slot('data-packs',
                                  projects=[Configuration.DBASE(pkgs)])
        os.chdir('build')
        slot.checkout()
        os.chdir(os.pardir)

        for pkg in pkgs:
            assert exists(join('build', pkg.baseDir)), 'missing %s' % pkg.baseDir
        assert exists(join('build', 'DBASE', 'AppConfig', 'v3r198'))
        assert not islink(join('build', 'DBASE', 'AppConfig', 'v3r198'))
        # these are signatures of a build
        assert exists(join('build', 'DBASE', 'AppConfig', 'v3r198', 'cmt', 'Makefile'))
        assert isdir(join('build', 'DBASE', 'AppConfig', 'v3r198', os.environ['CMTCONFIG']))

        assert islink(join('build', 'DBASE', 'AppConfig', 'v3r196'))

        assert islink(join('build', 'DBASE', 'Gen'))

        assert not islink(join('build', 'DBASE', 'Det'))
        assert not islink(join('build', 'DBASE', 'Det', 'SQLDDDB'))
        assert not islink(join('build', 'DBASE', 'Det', 'SQLDDDB', 'head'))
        assert exists(join('build', 'DBASE', 'Det', 'SQLDDDB', 'head', 'cmt'))
        assert islink(join('build', 'DBASE', 'Det', 'SQLDDDB', 'v7r10'))
        assert islink(join('build', 'DBASE', 'Det', 'SQLDDDB', 'v7r999'))
        assert os.readlink(join('build', 'DBASE', 'Det', 'SQLDDDB', 'v7r999')) == 'head'
        assert islink(join('build', 'DBASE', 'Det', 'SQLDDDB', 'v999r999'))
        assert os.readlink(join('build', 'DBASE', 'Det', 'SQLDDDB', 'v999r999')) == 'head'

        # we do not create PARAM if not requested
        assert not exists(join('build', 'PARAM'))

def test_stack_checkout_datapkg_old():
    '''checkout a data package within a slot'''
    if not which('getpack'):
        raise nose.SkipTest

    Package = Configuration.Package

    mlh = MockLoggingHandler()
    Configuration.__log__.addHandler(mlh)

    with TemporaryDir(chdir=True):
        pkgs = [Package(name='AppConfig', version='v3r198'),
                Package(name='Det/SQLDDDB', version='HEAD')]
        slot = Configuration.Slot('dummy', projects=[Configuration.DBASE(pkgs)])
        with Utils.chdir('build', create=True):
            slot.checkout()

        for pkg in pkgs:
            assert exists(join('build', pkg.baseDir)), 'missing %s' % pkg.baseDir
        assert exists(join('build', 'DBASE', 'AppConfig', 'v3r198'))
        assert not islink(join('build', 'DBASE', 'AppConfig', 'v3r198'))
        # these are signatures of a build
        assert exists(join('build', 'DBASE', 'AppConfig', 'v3r198', 'cmt', 'Makefile'))
        assert isdir(join('build', 'DBASE', 'AppConfig', 'v3r198', os.environ['CMTCONFIG']))

        assert islink(join('build', 'DBASE', 'AppConfig', 'v3r196'))

        assert islink(join('build', 'DBASE', 'Gen'))

        assert not islink(join('build', 'DBASE', 'Det'))
        assert not islink(join('build', 'DBASE', 'Det', 'SQLDDDB'))
        assert not islink(join('build', 'DBASE', 'Det', 'SQLDDDB', 'head'))
        assert exists(join('build', 'DBASE', 'Det', 'SQLDDDB', 'head', 'cmt'))
        assert islink(join('build', 'DBASE', 'Det', 'SQLDDDB', 'v7r10'))
        assert islink(join('build', 'DBASE', 'Det', 'SQLDDDB', 'v7r999'))
        assert os.readlink(join('build', 'DBASE', 'Det', 'SQLDDDB', 'v7r999')) == 'head'
        assert islink(join('build', 'DBASE', 'Det', 'SQLDDDB', 'v999r999'))
        assert os.readlink(join('build', 'DBASE', 'Det', 'SQLDDDB', 'v999r999')) == 'head'

        # we do not create PARAM if not requested
        assert not exists(join('build', 'PARAM'))
