import os.path
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

import aufbau

version = aufbau.VERSION

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main([self.pytest_args])
        sys.exit(errno)


setup(
    name='aufbau',
    packages=['aufbau'],
    version=version,
    description='A toolkit for writing build scripts for .NET projects in Python.',
    author='James McKay',
    author_email='code@jamesmckay.net',
    keywords=['dotnet', 'build'],
    url='https://github.com/jammycakes/aufbau',
    download_url = 'https://github.com/jammycakes/aufbau/archive/{0}.tar.gz'.format(version),
    license='MIT',
    install_requires=[
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': [
            'aufbau=aufbau.core.command:main'
        ]
    },
    tests_require=['pytest'],
    cmdclass = {'test': PyTest},
)