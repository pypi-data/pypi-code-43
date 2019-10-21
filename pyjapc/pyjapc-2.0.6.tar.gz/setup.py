#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import os
import setuptools
import shutil

from setuptools.command.install import install as _install


def get_version_from_init():
    init_file = os.path.join(
        os.path.dirname(__file__), 'pyjapc', '__init__.py'
    )
    with open(init_file, 'r') as fd:
        for line in fd:
            if line.startswith('__version__'):
                return ast.literal_eval(line.split('=', 1)[1].strip())


# Custom install function to install and register with cmmnbuild-dep-manager
class install(_install):
    user_options = _install.user_options + [
        ('no-jars', None, 'do not register with cmmnbuild-dep-manager')
    ]

    def initialize_options(self):
        self.no_jars = False
        _install.initialize_options(self)

    def run(self):
        if not self.no_jars:
            import cmmnbuild_dep_manager
            mgr = cmmnbuild_dep_manager.Manager()
            mgr.install('pyjapc')
            print('registered pyjapc with cmmnbuild-dep-manager')
        _install.run(self)


# Function to deploy Sphinx documentation
class deploy_sphinx(setuptools.Command):
    description = 'Deploy Sphinx documentation'
    user_options = [
        ('source-dir=', None, 'source directory'),
        ('dest-dir=', None, 'destination directory'),
        ('chmod-files=', None, 'mode for files (default 0644)'),
        ('chmod-dirs=', None, 'mode for dirs (default 0755)')
    ]

    def initialize_options(self):
        self.source_dir = None
        self.dest_dir = None
        self.chmod_files = '0644'
        self.chmod_dirs = '0755'

    def finalize_options(self):
        if self.source_dir is None:
            raise Exception('Parameter --source-dir is missing')
        if self.dest_dir is None:
            raise Exception('Parameter --dest-dir is missing')
        if not os.path.isdir(self.source_dir):
            raise Exception('Source directory does not exist')
        if not os.path.isdir(self.dest_dir):
            raise Exception('Destination directory does not exist')

        self.source_dir = os.path.abspath(self.source_dir)
        self.dest_dir = os.path.abspath(self.dest_dir)
        self.chmod_files = int(self.chmod_files, 8)
        self.chmod_dirs = int(self.chmod_dirs,  8)

    def run(self):
        # Delete everything in destination directory
        for item in os.listdir(self.dest_dir):
            dest_path = os.path.join(self.dest_dir, item)
            print('deleting {0}'.format(dest_path))
            if os.path.isdir(dest_path):
                shutil.rmtree(dest_path)
            else:
                os.remove(dest_path)

        # Copy everything from source directory to destination directory
        for item in os.listdir(self.source_dir):
            source_path = os.path.join(self.source_dir, item)
            dest_path = os.path.join(self.dest_dir, item)
            print('copying {0} -> {1}'.format(source_path, dest_path))
            if os.path.isdir(source_path):
                shutil.copytree(source_path, dest_path)
            else:
                shutil.copy(source_path, dest_path)

        # Set permissions
        for root, dirs, files in os.walk(self.dest_dir):
            for item in files:
                item_path = os.path.join(root, item)
                print('change mode to 0{0:o} for {1}'.format(self.chmod_files, item_path))
                os.chmod(item_path, self.chmod_files)
            for item in dirs:
                item_path = os.path.join(root, item)
                print('change mode to 0{0:o} for {1}'.format(self.chmod_dirs,  item_path))
                os.chmod(item_path, self.chmod_dirs)


setuptools.setup(
    name='pyjapc',
    version=get_version_from_init(),
    description='Python to FESA/LSA/INCA interface via JAPC',
    author='CERN MD Scripting Tools Community',
    author_email='MD-scripting-tools@cern.ch',
    license='MIT',
    url='https://gitlab.cern.ch/scripting-tools/pyjapc',
    packages=['pyjapc'],
    package_data={
        'pyjapc': ['pyjapc/*.pyi'],
    },
    install_requires=[
        'JPype1>=0.6.1,<0.7.0',
        'cmmnbuild-dep-manager>=2.1.0',
        'numpy',
        'six',
        'pytz'
    ],
    extras_require={
        'testing': ['pytest'],
        'doc': ['sphinx'],
    },
    cmdclass={
        'install': install,
        'deploy_sphinx': deploy_sphinx
    }
)
