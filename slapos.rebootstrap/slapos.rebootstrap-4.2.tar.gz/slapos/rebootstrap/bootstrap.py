import os, sys

class FakeSysExecutable(object):

  def __init__(self, python):
    self.executable = python

  def __getattr__(self, attr):
    return getattr(sys, attr)

def get_distributions():
  from pkg_resources import get_distribution
  distributions = ['setuptools', 'zc.buildout']
  try:
    import slapos.libnetworkcache
  except ImportError:
    pass
  else:
    distributions.append('slapos.libnetworkcache')
  return map(get_distribution, distributions)

def setup_script(path, python=sys.executable):
  from zc.buildout import easy_install
  try:
    if sys.executable != python:
      easy_install.sys = FakeSysExecutable(python)
    easy_install.scripts(
      ((os.path.realpath(path), 'zc.buildout.buildout', 'main'),),
      get_distributions(),
      python)
  finally:
    easy_install.sys = sys

def main():
  import shutil, subprocess, tempfile, zipfile
  eggs_dir = sys.argv[2]
  cache = sys.argv[3]
  # Install setuptools.
  src = os.path.join(cache, sys.argv[4].replace('==', '-') + '.zip')
  tmp = tempfile.mkdtemp()
  try:
    with zipfile.ZipFile(src) as zip_file:
      zip_file.extractall(tmp)
    src, = os.listdir(tmp)
    subprocess.check_call((sys.executable, 'setup.py', '-q', 'bdist_egg',
                          '--dist-dir', tmp), cwd=os.path.join(tmp, src))
    egg = os.listdir(tmp)
    egg.remove(src)
    egg, = egg
    dst = os.path.join(eggs_dir, egg)
    os.path.exists(dst) or shutil.move(os.path.join(tmp, egg), dst)
  finally:
    shutil.rmtree(tmp)
  sys.path.insert(0, dst)
  # Install other requirements given on command line.
  from pkg_resources import working_set, require
  from setuptools.command import easy_install
  reqs = sys.argv[5:]
  easy_install.main(['-mZqNxd', eggs_dir, '-f', cache] + reqs)
  working_set.add_entry(eggs_dir)
  for req in reqs:
    require(req)
  # Generate bin/buildout-rebootstrap script.
  setup_script(sys.argv[1])

if __name__ == '__main__':
  sys.exit(main())
