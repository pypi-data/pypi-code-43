from __future__ import print_function
from setuptools import setup, find_packages
# from fake_rpi.version import __version__ as VERSION
from build_utils import BuildCommand
from build_utils import PublishCommand
from build_utils import BinaryDistribution
from build_utils import SetGitTag
from build_utils import get_pkg_version

import os
cmd = "protoc --proto_path=../cpp/gecko/protobuf  --python_out=pygeckopb ../cpp/gecko/protobuf/msgs.proto"
os.system(cmd)

VERSION = get_pkg_version('pygeckopb/__init__.py')
PACKAGE_NAME = 'pygeckopb'
BuildCommand.pkg = PACKAGE_NAME
PublishCommand.pkg = PACKAGE_NAME
PublishCommand.version = VERSION
BuildCommand.py2 = False
SetGitTag.version = VERSION


setup(
    author='Kevin Walchko',
    author_email='walchko@users.noreply.github.com',
    name=PACKAGE_NAME,
    version=VERSION,
    description='pygecko messaging with protobuf',
    long_description=open('readme.md').read(),
    long_description_content_type='text/markdown',
    url='http://github.com/gecko-robotics/{}'.format(PACKAGE_NAME),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        # 'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
    ],
    license='MIT',
    keywords=['ros', 'protobuf', 'protocol buffer'],
    packages=find_packages('.'),
    install_requires=['build_utils'],
    cmdclass={
        'make': BuildCommand,
        'publish': PublishCommand,
        'git': SetGitTag
    }
)
