import os
import sys

from setuptools import setup
from setuptools.command.install import install

# Load version number
exec(open('stakion/version.py').read())

def readme():
    """print long description"""
    with open('README.rst') as f:
        return f.read()

class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != __version__:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, __version__
            )
            sys.exit(info)
 
setup(
    name='stakion-logger',
    version=__version__,
    long_description=readme(),
    url='https://stakion.io/',
    author='Jacques Verre',
    author_email='jacques.verre@stackion.io',
    license='LICENSE.txt',
    description='Logger for stakion.',
    packages=['stakion'],
    install_requires=[
          'requests_futures',
          'python-socketio'
    ],
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)
