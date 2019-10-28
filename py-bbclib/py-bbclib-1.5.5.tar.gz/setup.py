import subprocess
import sys
import os
from os import path
from setuptools import setup
from setuptools.command.install import install

VERSION = "1.5.5"

here = path.abspath(path.dirname(__file__))

with open('README.rst') as f:
    readme = f.read()


class MyInstall(install):
    def run(self):
        try:
            subprocess.call(['python', 'prepare.py'], cwd=here)
        except Exception as e:
            print(e)
            exit(1)
        else:
            install.run(self)


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != "v%s" % VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, "v%s" % VERSION
            )
            sys.exit(info)


bbclib_requires = [
    'pyOpenSSL>=16.2.0',
    'cryptography>=2.1.4',
    'msgpack-python>=0.4.8',
    'bson'
]

bbclib_packages = ['bbclib', 'bbclib.libs', 'bbclib.compat']

bbclib_commands = [
    'install_libbbcsig',
    'copy_libbbcsig'
]

bbclib_classifiers = [
                    'Development Status :: 4 - Beta',
                    'Programming Language :: Python :: 3.5',
                    'Programming Language :: Python :: 3.6',
                    'Programming Language :: Python :: 3.7',
                    'Topic :: Software Development']

setup(
    name='py-bbclib',
    version=VERSION,
    description='The library of BBc-1 transaction data structure definition',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/beyond-blockchain/py-bbclib',
    author='beyond-blockchain.org',
    author_email='bbc1-dev@beyond-blockchain.org',
    license='Apache License 2.0',
    classifiers=bbclib_classifiers,
    cmdclass={'install': MyInstall, 'verify': VerifyVersionCommand},
    packages=bbclib_packages,
    scripts=bbclib_commands,
    install_requires=bbclib_requires,
    zip_safe=False)

