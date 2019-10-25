# -*- coding: utf-8 -*-
"""
Mapping Learning is still in an early stage of development. Will you dare installing
an alpha version of a software? It is a bit more complex than usual, but Mapping Learning
is worth it... and it will be easier in the future.

**Dependancies**

	# apt-get install python-pip

	# apt-get install libblas-dev liblapack-dev libatlas-base-dev gfortran

**Get source code**

**Installing**
"""
from __future__ import print_function

import inspect
import sys
import os
import shutil

from setuptools.command.test import test as TestCommand
from setuptools.command.install import install as _install
from setuptools import setup, find_packages

class SetupError(Exception):
    """ Exception raised during Setup"""
    pass

SETUP_ERROR = SetupError("""
        You should run setup.py in maplearn code source directory, ie:
        cd /path/to/maplearn
        python setup.py install""")

def get_ori(path):
    """
    Get list of original configuration files to edit when installing maplearn

    Arg:
        * path (str): path to look for original configuration files

    Returns:
        list: list of original configuration files
    """
    return [os.path.join(path, i) for i in os.listdir(path) \
            if os.path.splitext(i)[-1] == '.ORI']

def update_cfg_file(cfg_file, path):
    """
    Configuration files contain some absolute paths to datasets (needed to run
    included examples). This function sets these absolute paths.

    Args:
        * cfg_file (str): path to the configuration file to edit
        * path (str): path to set
    """
    path = os.path.normpath(path)
    # needed for windows compatibility
    path = path.replace('\\', '\\\\')
    with open(cfg_file) as __file:
        with open(cfg_file[:-4], 'w') as __file_out:
            for line in __file:
                line = line.format(path=path)
                __file_out.write(line)
    print("Configuration file %s updated" % cfg_file)

class PyTest(TestCommand):
    """
    Class to run unit tests with the installer
    """
    test_package_name = 'maplearn'
    test_suite = True
    def finalize_options(self):
        TestCommand.finalize_options(self)
        _test_args = [
            #'--pep8', # uncomment to assert pep8
            '--ignore=env',
        ]
        extra_args = os.environ.get('PYTEST_EXTRA_ARGS')
        if extra_args is not None:
            _test_args.extend(extra_args.split())
        self.test_args = _test_args

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

class Install(_install):
    """
    Installation class with some post install tasks
    """
    def run(self):
        _install.run(self)
        self._post_install()

    def _post_install(self):
        """
        Post install tasks : edit configuration files
        """
        print("Running post install task")
        path = self.install_lib
        # in package directory
        for file_path in get_ori(path + 'maplearn/examples'):
            update_cfg_file(file_path, path)
        # application path
        dir_app = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe())))
        # in code source directory
        for file_path in get_ori('maplearn/examples'):
            update_cfg_file(file_path, dir_app)
        # create tmp directory (for unit tests...)
        if os.path.exists('tmp'):
            shutil.rmtree('tmp')
        os.mkdir('tmp')

if __name__ == '__main__':

    try:
        from maplearn import __version__
    except ImportError:
        raise SETUP_ERROR

    if os.path.split(sys.argv[0])[0] not in ['', '.']:
        raise SETUP_ERROR

    requirements = open('requirements.txt').read()
    if os.environ.get('READTHEDOCS') == 'True':
        requirements = requirements.replace('gdal', '#gdal')
    setup(
        name='maplearn',
        version=__version__,
        test_suite="test",
        packages=find_packages(exclude=['test']),
        description='Mapping Learning',
        url='https://bitbucket.org/thomas_a/maplearn/',
        author="Alban Thomas",
        author_email="alban.thomas@univ-rennes2.fr",
        license='LGPL',
        platforms='any',
        long_description=open('README.md').read(),
        install_requires=requirements,
        cmdclass={'install': Install, 'test': PyTest},
        entry_points={
            'console_scripts': [
                'maplearn=maplearn.run:run',
                'maplearn_example=maplearn.run_example:main',
                'maplearn_gui=maplearn.run_gui:main'
            ],
        },
        classifiers=[
                "Development Status :: 3 - Alpha",
                "Environment :: Console",
                "Environment :: Win32 (MS Windows)",
                "Environment :: X11 Applications",
                "Framework :: Sphinx",
                "Intended Audience :: Education",
                "Intended Audience :: End Users/Desktop",
                "Intended Audience :: Science/Research",
                "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
                "Natural Language :: French",
                "Programming Language :: Python",
                "Programming Language :: Python :: 2",
                "Programming Language :: Python :: 2.7",
                "Programming Language :: Python :: 3",
                "Programming Language :: Python :: 3.5",
                "Programming Language :: Python :: 3.6",
                "Programming Language :: Python :: 3.7",
                "Topic :: Education",
                "Topic :: Scientific/Engineering :: Artificial Intelligence",
                "Topic :: Scientific/Engineering :: Atmospheric Science",
        ],
        include_package_data=True,
        zip_safe=False,
        )
