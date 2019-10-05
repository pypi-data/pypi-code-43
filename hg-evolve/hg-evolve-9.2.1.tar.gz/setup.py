import os
from distutils.core import setup
from os.path import dirname, join

META_PATH = 'hgext3rd/evolve/metadata.py'

def get_metadata():
    meta = {}
    fullpath = join(dirname(__file__), META_PATH)
    with open(fullpath, 'r') as fp:
        exec(fp.read(), meta)
    return meta

def get_version():
    '''Read version info from a file without importing it'''
    return u'%s' % get_metadata()['__version__']

def min_hg_version():
    '''Read version info from a file without importing it'''
    return get_metadata()['minimumhgversion']

py_modules = [
    'hgext3rd.serverminitopic',
]
py_packages = [
    'hgext3rd',
    'hgext3rd.evolve',
    'hgext3rd.evolve.thirdparty',
    'hgext3rd.topic',
]
py_packagedir = {
    'hgext3rd': join(dirname(__file__), 'hgext3rd')
}

py_versions = '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, <4'

if os.environ.get('INCLUDE_INHIBIT'):
    py_modules.append('hgext3rd.evolve.hack.inhibit')
    py_modules.append('hgext3rd.evolve.hack.directaccess')

setup(
    name='hg-evolve',
    version=get_version(),
    author='Pierre-Yves David',
    author_email='pierre-yves.david@ens-lyon.org',
    maintainer='Pierre-Yves David',
    maintainer_email='pierre-yves.david@ens-lyon.org',
    url='https://www.mercurial-scm.org/doc/evolution/',
    description='Flexible evolution of Mercurial history.',
    long_description=open(join(dirname(__file__), 'README')).read(),
    keywords='hg mercurial',
    license='GPLv2+',
    py_modules=py_modules,
    packages=py_packages,
    package_dir=py_packagedir,
    python_requires=py_versions
)
