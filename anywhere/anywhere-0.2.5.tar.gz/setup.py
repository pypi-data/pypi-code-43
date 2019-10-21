# -*- coding:utf-8 -*-
import distutils
import os
import subprocess
import sys

from setuptools import find_packages, setup


os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


with open('README.md') as fh:
    README = fh.read()


class PylintCommand(distutils.cmd.Command):
    """A custom command to run Pylint on all Python source files."""

    description = 'Run pyint linter.'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run command."""
        command = [
            'pylint', '--rcfile=toolscfg/pylintrc',
            # Those three are only cluttering the results, will be fixed some day.
            '--disable', 'missing-module-docstring',
            '--disable', 'missing-function-docstring',
            '--disable', 'missing-class-docstring',
            'anywhere',
        ]

        self.announce(f'Running command: {" ".join(command)}', level=distutils.log.INFO)

        try:
            subprocess.check_call(command)
        except subprocess.CalledProcessError as ex:
            sys.exit(ex.returncode)


class CleanCommand(distutils.cmd.Command):
    """A custom command to clean build / test artifacts."""

    description = 'Clean artifacts (reports, builds...).'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run command."""
        commands = (
            ['rm', '-Rf', '.pytest_cache'],
            ['rm', '-Rf', 'htmlcov'],
            ['rm', '-Rf', 'htmltest'],
            ['rm', '-f', '.coverage'],
            ['rm', '-f', 'coverage.xml'],
            ['rm', '-f', 'report.xml'],
            ['rm', '-Rf', 'build'],
            ['rm', '-Rf', 'dist'],
        )

        for command in commands:
            self.announce(f'Running command: {" ".join(command)}', level=distutils.log.INFO)
            try:
                subprocess.check_call(command)
            except subprocess.CalledProcessError as ex:
                sys.exit(ex.returncode)


class ProtocCommand(distutils.cmd.Command):
    """A custom command to clean build / test artifacts."""

    description = 'Clean artifacts (reports, builds...).'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run command."""
        commands = (
            ['protoc', '-I', '.', '--python_out', '.', 'anywhere/anywhere.proto'],
            ['mv', 'anywhere/anywhere_pb2.py', 'anywhere/protobuf3/'],
        )

        for command in commands:
            self.announce(f'Running command: {" ".join(command)}', level=distutils.log.INFO)
            try:
                subprocess.check_call(command)
            except subprocess.CalledProcessError as ex:
                sys.exit(ex.returncode)


setup(
    name='anywhere',
    use_scm_version=True,
    description='Turn logical sentences into serializable, executable queries.',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/mlga/anywhere',
    author='mlga',
    author_email='github@mlga.io',
    license='MIT',
    keywords='filtering sqlalchemy query graphene protobuf',
    setup_requires=[
        'pytest-runner~=5.1',
        'setuptools_scm~=3.3',
    ],
    install_requires=[],
    tests_require=[
        'pytest~=5.0',
        'pytest-cov~=2.7',
        'pytest-html~=1.20',
    ],
    extras_require={
        'sqlalchemy': [
            'SQLAlchemy~=1.3.0',
        ],
        'graphene': [
            'marshmallow~=2.19',
            'graphene~=2.1',
        ],
        'protobuf': [
            'protobuf~=3.9',
        ],
        'develop': [
            'pylint~=2.3',
            'pytest~=5.0',
            'pytest-cov~=2.7',
            'pytest-html~=1.20',
        ],
    },
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    platforms='any',
    zip_safe=False,
    cmdclass={
        'pylint': PylintCommand,
        'clean': CleanCommand,
        'protoc': ProtocCommand,
    },
    python_requires='>=3.7',
)
