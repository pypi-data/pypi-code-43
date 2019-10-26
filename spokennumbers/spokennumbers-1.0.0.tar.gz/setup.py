import sys
from setuptools import setup, find_packages

sys.path.append('spokennumbers')
from _info import (
    __version__,
    __author__,
    __maintainer__,
    __email__,
    __status__,
    __url__,
    __license__
)
sys.path.remove('spokennumbers')
with open('README.rst') as readme_file:
    long_description = readme_file.read()

setup(
    name='spokennumbers',
    version=__version__,
    author=__author__,
    author_email=__email__,
    description=\
        'Generate spoken numbers mp3 files used for Memory Competitions',
    long_description=long_description,
    license=__license__,
    keywords='spoken numbers iam wmc memory competition memorization',
    url=__url__,
    packages=find_packages(exclude=['tests']),
    package_data={
        'spokennumbers': ['default/*.wav']
    },
    entry_points=dict(
        console_scripts=['spokennumbers = spokennumbers.__main__:main',
                         'spoken = spokennumbers.__main__:main'],
    ),
    install_requires=['pydub'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Version Control :: Git',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython'
    ]
)
