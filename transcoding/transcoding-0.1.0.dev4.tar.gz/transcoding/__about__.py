"""
Description of project with title, state and further constants
"""
import os
__all__ = [
    "__version__",
    # "__title__",
    "__summary__",
    "__keywords__",
    "__uri__",
    "__author__",
    "__email__",
    "__license__",
    "__copyright__",
    "__python_requires__",
    "__dependencies__",
    "__classifiers__",
]
__version__ = '0.1.0.dev4'
# __title__ = os.path.basename(os.path.abspath('.'))  # problematic
__summary__ = "transcodings for standardized file in- and output"
__keywords__ = "file input output transcoding standardize"
__uri__ = 'https://gitlab.mpcdf.mpg.de/dboe/transcoding'
__author__ = "Daniel Boeckenhoff"
__email__ = "daniel.boeckenhoff@ipp.mpg.de"
__license__ = "Apache Software License"
__copyright__ = "2018 %s" % __author__
__python_requires__ = '>=2.7'
__dependencies__ = [
    'pathlib2;python_version<"3.0"',
    'pathlib;python_version>="3.0"',
    'parse',
    'more_itertools',
    'future',
    ]
__classifiers__ = [
    # find the full list of possible classifiers at https://pypi.org/classifiers/
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: {0}'.format(__license__),
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
]
