#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
PY3K = sys.version_info[0] == 3
import os
import posixpath
import glob


from setuptools import setup, find_packages, Extension

# see bootstrap for installing thoses requirements
# using easy_install (err Distribute)
try:
    import yaml 
except ImportError as e:
    raise ImportError("Please install pyyaml.")

workdir = os.getcwd()
admindir = posixpath.join(workdir, 'admin')

#from pkg_resources import resource_stream

# Do import buildutils commands if available!
try:
    import buildutils
except ImportError:
    print('Consider installing the buildutils module!')

libs = find_packages(where='lib')

# Meta info in YAML data format for improved readability
meta = yaml.load(open(posixpath.join(admindir, 'PKG-INFO.in')))

scripts_data = glob.glob('tools/schevo-*') + ['tools/httpserver.py']

staticdir = posixpath.abspath(os.path.join(admindir, 'static'))

classifiers = [
    (str(item)) for item in open(posixpath.abspath(os.path.join(staticdir, \
    'classifiers.txt'))).read().split('\n') if item is not '']

setup(
    name=meta['Name'],
    version=meta['Version'],
    description=meta['Summary'], 
    long_description=meta['Description'],
    author=meta['Author'],
    author_email=meta['Author-email'],
    license=meta['License'],
    keywords=meta['Keywords'],
    url=meta['Homepage'],
    #maintainer=meta['Maintainer'],
    #maintainer_email=meta['Maintainer-email'],
    scripts=scripts_data,

    # Include stuff which belong in SVN or mentioned in MANIFEST.in
    include_package_data=True,

    # Location where packages lives
    package_dir={'': 'lib'},
    packages=libs,

    # Package classifiers are read from static/classifiers.txt
    classifiers=classifiers,

    # Add Cython compiled extensions
    #cmdclass={'build_ext': build_ext},
    #ext_modules=ext_modules,
    
    # Minimal packages required when doing `python setup.py install`.
    install_requires=[
        #'Django>=1.11.17',  # Maintainers should not need this :-)
        'pytz>=2017.2',     # django dependency (optional)
        #'Beaker>=1.9.0',    # memcached support (optional)
        #'configobj>=4.7.2', # in notmm.utils.configparse (required)
        'argparse>=1.1',    # Used by tools/httpserver.py (required)
        #'demjson>=2.2.4',   # JSON support (optional)
        'Mako>=1.1.0',      # Mako template backend (optional)
        #'feedparser>=5.1.2'# RSS 2.0 parsing (optional)
        #'docutils>=0.8.1',         # Docutils support (optional)
        #'python-epoll>=1.0',       # For epoll support Linux only (optional)
        #'pytidylib>=0.2.1',        # PyTidyLib support      (optional) 
        #'python-memcached>=1.58',  # memcached support      (optional)
        'werkzeug>=0.16',         # Werkzeug  support      (optional) 
        #'gevent==1.4.0',            # Gevent    support      (optional)
        'ZODB>=5.3.0',              # ZODB backend support   (optional)
        'ZEO>=5.1.0',               # ZEO backend support    (optional)
        #'Elixir>=0.7.1',            # Elixir support         (optional)
        #'libschevo>=4.1',         # Schevo backend support (required)
        #'blogengine2>=0.9.6',       # BlogEngine 2.0 support (optional)
        'uWSGI>=2.0.18',          # uWSGI support          (required)
        #'django-hotsauce-oauthclient>=0.3', # Experimental OAuth 2.0 support
        'transaction>=2.4',         # transaction support    (required)
        'persistent>=4.4.3'         # persistence support    (required)
    ],
    zip_safe=False
)

