##############################################################################
#
# Copyright (c) 2010-2017 ViFiB SARL and Contributors.
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

import logging, os, shutil, subprocess, sys, tempfile
from zc.buildout import easy_install, UserError


class extension(object):

  def __init__(self, buildout):
    self.buildout = buildout
    # fetch section to build python (default value is 'buildout')
    self.python_section = buildout['buildout']['python'].strip()
    self.wanted_python = buildout[self.python_section]['executable']
    if sys.executable != self.wanted_python:
      self.hook('_setup_directories')
    elif buildout._parts:
      self._frozen = frozenset(buildout._parts)
      self.hook('_compute_part_signatures')

  def hook(self, attr):
    buildout = self.buildout
    getattr(buildout, attr)
    def wrapper(*args, **kw):
      delattr(buildout, attr)
      return getattr(self, attr)(*args, **kw)
    setattr(buildout, attr, wrapper)

  def _setup_directories(self):
    logger = logging.getLogger(__name__)
    buildout = self.buildout
    logger.info(
      "Make sure that the section %r won't be reinstalled after rebootstrap."
      % self.python_section)
    # We hooked in such a way that all extensions are loaded. Do not reload.
    buildout._load_extensions
    buildout._load_extensions = lambda: None
    # workaround for the install command,
    # which ignores dependencies when parts are specified
    # (the only sections we have accessed so far are those that are required
    #  to build the wanted Python)
    buildout.install(buildout._parts) # [self.python_section]

    logger.info("""
************ REBOOTSTRAP: IMPORTANT NOTICE ************
bin/buildout is being reinstalled right now, as new python:
  %(wanted_python)s
is available, and buildout is using another python:
  %(running_python)s
Buildout will be restarted automatically to have this change applied.
************ REBOOTSTRAP: IMPORTANT NOTICE ************
""" % dict(wanted_python=self.wanted_python, running_python=sys.executable))

    installed = sys.argv[0]
    new_bin = installed + '-rebootstrap'
    if not os.path.exists(new_bin):
      from .bootstrap import get_distributions, setup_script
      if subprocess.call((self.wanted_python, '-c',
          'import sys; sys.exit(sys.version_info[:2] == %r)'
          % (sys.version_info[:2],))):
        setup_script(new_bin, self.wanted_python)
      else:
        # With a different version of Python,
        # we must reinstall required eggs from source.
        from pkg_resources import resource_string
        with Cache(buildout['buildout']) as cache:
          subprocess.check_call([self.wanted_python, '-c',
            resource_string(__name__, 'bootstrap.py'),
            new_bin, cache._dest, cache.tmp,
            ] + list(map(cache, get_distributions())))

    shutil.copy(new_bin, installed)
    os.execv(self.wanted_python, [self.wanted_python] + sys.argv)

  def _compute_part_signatures(self, install_parts):
    # Skip signature check for parts that were required to build the wanted
    # Python. Signatures differ when switching to a different version.
    buildout = self.buildout
    buildout._compute_part_signatures(install_parts)
    installed_part_options = buildout.installed_part_options
    for part in self._frozen.intersection(install_parts):
      if part in installed_part_options:
        buildout[part]['__buildout_signature__'] = \
          installed_part_options[part]['__buildout_signature__']


class Cache(easy_install.Installer):

  def __init__(self, buildout):
    easy_install.Installer.__init__(self,
      buildout['eggs-directory'],
      buildout.get('find-links', '').split())

  def __enter__(self):
    self.tmp = self._download_cache or tempfile.mkdtemp('get_dist')
    return self

  def __exit__(self, t, v, tb):
    if self.tmp is not self._download_cache:
      shutil.rmtree(self.tmp)
    del self.tmp

  def __call__(self, dist):
    req = dist.as_requirement()
    cache = self._download_cache
    if cache:
      from pkg_resources import SOURCE_DIST
      for avail in self._index[dist.project_name]:
        if (avail.version == dist.version and
            avail.precedence == SOURCE_DIST and
            cache == os.path.dirname(avail.location)):
          return str(req)
    avail = self._obtain(req, True)
    if avail is None:
      raise UserError("Couldn't find a distribution for %r" % str(req))
    if self._fetch(avail, self.tmp, cache) is None:
      raise UserError("Couldn't download distribution %s." % avail)
    return str(req)
