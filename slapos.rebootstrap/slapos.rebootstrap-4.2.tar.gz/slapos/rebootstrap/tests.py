##############################################################################
#
# Copyright (c) 2010 ViFiB SARL and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from zope.testing import renormalizing
import doctest
import pkg_resources
import re
import shutil
import sys
import unittest
import zc.buildout
import zc.buildout.testing
import zc.buildout.tests

def _setUp(cp, mkdir, write, buildout, sample_buildout, **kw):
  cp(buildout, buildout + '-orig')
  mkdir(sample_buildout, 'recipes')
  write(sample_buildout, 'recipes', 'setup.py', """
from setuptools import setup

setup(
  name = "recipes",
  entry_points = {'zc.buildout':[
    'pyinstall = pyinstall:Pyinstall',
    'pyalreadyinstalled = pyalreadyinstalled:PyAlreadyInstalled',
    'pyshow = pyshow:Pyshow',
  ]},
  )
""")
  write(sample_buildout, 'recipes', 'README.txt', " ")
  write(sample_buildout, 'recipes', 'pyinstall.py', """
import os, zc.buildout, shutil, sys

class Pyinstall:

  def __init__(self, buildout, name, options):
    self.options = options
    options['executable'] = os.path.join(buildout['buildout'][
      'parts-directory'], name, 'bin', 'python')

  def install(self):
    python = self.options['executable']
    if not os.path.exists(python):
      d = os.path.dirname(python)
      os.path.exists(d) or os.makedirs(d)
      shutil.copy(sys.executable, python)
    return []

  update = install
""")
  write(sample_buildout, 'recipes', 'pyalreadyinstalled.py', """
import os, zc.buildout, shutil, sys

class PyAlreadyInstalled:

  def __init__(self, buildout, name, options):
    print "Using already installed", sys.executable
    options['executable'] = sys.executable

  def install(self):
    return []

  update = install
""")
  write(sample_buildout, 'recipes', 'pyshow.py', """
import os, zc.buildout, shutil, sys

class Pyshow:

  def __init__(self, buildout, name, options):
    pass

  def install(self):
    print 'Running with:', sys.executable
    return []

  update = install
""")
  write(sample_buildout, 'buildout.cfg', """
[buildout]
develop = recipes
parts =
""")

def setUp(test):
  zc.buildout.testing.buildoutSetUp(test)
  zc.buildout.testing.install_develop('slapos.rebootstrap', test)
  test.globs['cp'] = shutil.copy
  _setUp(**test.globs)

def test_suite():
  # Note: Doctests are used, as this is the good way to test zc.buildout based
  #       applications. And zc.buildout.testing.buildoutSetUp does *NOT* support
  #       non-doctest suites
  kwargs = dict(setUp=setUp,
      tearDown=zc.buildout.testing.buildoutTearDown,
      checker=renormalizing.RENormalizing([
                        (re.compile('--prefix=\S+sample-buildout'),
                         '--prefix=/sample_buildout'),
                        (re.compile('\s/\S+sample-buildout'),
                         ' /sample_buildout'),
                        (re.compile(sys.executable),
                         '/system_python'),
                        zc.buildout.testing.normalize_path,
                        zc.buildout.testing.not_found,
                        ]),
    )
  test_list = []
  for text in pkg_resources.resource_listdir(__name__, '.'):
    if text.endswith('.txt'):
      test_list.append(doctest.DocFileSuite(text, **kwargs))
  suite = unittest.TestSuite(test_list)
  return suite
