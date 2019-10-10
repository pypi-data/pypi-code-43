import os
import sys

from setuptools import setup
from setuptools.command.install import install


VERSION = "0.5.2"

def readme():
    """print long description"""
    with open('README.rst') as f:
        return f.read()

class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(tag, VERSION)
            sys.exit(info)

setup(
    name='titus_optimize',
    author='titus',
    author_email='titus-ops@netflix.com',
    description="A package for optimizing placements of containers.",
    long_description=readme(),
    keywords='titus',
    url='https://github.com/Netflix-Skunkworks/titus-optimize',
    version=VERSION,
    setup_requires=['setupmeta'],
    python_requires='>=3.5',
    install_requires=['numpy>=1.16',
                      'pandas==0.24.1',
                      'cvxopt==1.2.3',
                      'lightgbm==2.2.3'],
    extras_require={
        'test': ['tox'],
    },
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)
