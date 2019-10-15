# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['data_extractor']

package_data = \
{'': ['*']}

install_requires = \
['cssselect>=1.0.3,<2.0.0',
 'jsonpath-rw-ext>=1.2,<2.0',
 'jsonpath-rw>=1.4.0,<2.0.0',
 'lxml>=4.3.0,<5.0.0']

extras_require = \
{'docs': ['sphinx>=2.2,<3.0'],
 'linting': ['black>=19.3b0,<20.0',
             'flake8>=3.7.8,<4.0.0',
             'isort>=4.3.21,<5.0.0',
             'mypy>=0.730,<0.731',
             'pytest>=5.2.0,<6.0.0',
             'doc8>=0.8.0,<0.9.0',
             'pygments>=2.4,<3.0',
             'flake8-bugbear>=19.8,<20.0',
             'blacken-docs>=1.3,<2.0'],
 'test': ['pytest>=5.2.0,<6.0.0', 'pytest-cov>=2.7.1,<3.0.0']}

setup_kwargs = {
    'name': 'data-extractor',
    'version': '0.5.0.dev1',
    'description': 'Combine XPath, CSS Selectors and JSONPath for Web data extracting.',
    'long_description': '# Data Extractor\n\n[![license](https://img.shields.io/github/license/linw1995/data_extractor.svg)](https://github.com/linw1995/data_extractor/blob/master/LICENSE)\n[![Pypi Status](https://img.shields.io/pypi/status/data_extractor.svg)](https://pypi.org/project/data_extractor)\n[![Python version](https://img.shields.io/pypi/pyversions/data_extractor.svg)](https://pypi.org/project/data_extractor)\n[![Package version](https://img.shields.io/pypi/v/data_extractor.svg)](https://pypi.org/project/data_extractor)\n[![PyPI - Downloads](https://img.shields.io/pypi/dm/data-extractor.svg)](https://pypi.org/project/data_extractor)\n[![GitHub last commit](https://img.shields.io/github/last-commit/linw1995/data_extractor.svg)](https://github.com/linw1995/data_extractor)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![Build Status](https://travis-ci.org/linw1995/data_extractor.svg?branch=master)](https://travis-ci.org/linw1995/data_extractor)\n[![codecov](https://codecov.io/gh/linw1995/data_extractor/branch/master/graph/badge.svg)](https://codecov.io/gh/linw1995/data_extractor)\n[![Documentation Status](https://readthedocs.org/projects/data-extractor/badge/?version=latest)](https://data-extractor.readthedocs.io/en/latest/?badge=latest)\n\nCombine **XPath**, **CSS Selectors** and **JSONPath** for Web data extracting.\n\n## Changelog\n\n### v0.5.0\n\n- 0056f37 Split AbstractExtractor into AbstractSimpleExtractor and AbstractComplexExtractor\n',
    'author': 'linw1995',
    'author_email': 'linw1995@icloud.com',
    'url': 'https://github.com/linw1995/data_extractor',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
