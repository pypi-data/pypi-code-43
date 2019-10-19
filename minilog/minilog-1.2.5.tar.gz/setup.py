# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['log', 'log.tests']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'minilog',
    'version': '1.2.5',
    'description': 'Minimalistic wrapper for Python logging.',
    'long_description': '[![Unix Build Status](https://img.shields.io/travis/jacebrowning/minilog/develop.svg?label=unix)](https://travis-ci.org/jacebrowning/minilog)\n[![Windows Build Status](https://img.shields.io/appveyor/ci/jacebrowning/minilog/develop.svg?label=windows)](https://ci.appveyor.com/project/jacebrowning/minilog)\n<br>\n[![Coverage Status](https://img.shields.io/coveralls/jacebrowning/minilog/develop.svg)](https://coveralls.io/r/jacebrowning/minilog)\n[![Scrutinizer Code Quality](https://img.shields.io/scrutinizer/g/jacebrowning/minilog.svg)](https://scrutinizer-ci.com/g/jacebrowning/minilog/?branch=develop)\n<br>\n[![PyPI Version](https://img.shields.io/pypi/v/minilog.svg)](https://pypi.org/project/minilog)\n[![PyPI License](https://img.shields.io/pypi/l/minilog.svg)](https://pypi.org/project/minilog) \n\n# Overview\n\nEvery project should utilize logging, but for simple use cases, this requires a bit too much boilerplate. Instead of including all of this in your modules:\n\n```python\nimport logging \n\nlogging.basicConfig(\n    level=logging.INFO,\n    format="%(levelname)s: %(name)s: %(message)s",\n)\n\nlog = logging.getLogger(__name__)\n\ndef greet(name):\n    log.info("Hello, %s!", name)\n```\n\nwith this package you can simply:\n\n```python\nimport log\n\ndef greet(name):\n    log.info("Hello, %s!", name)\n```\n\nIt will produce the exact same standard library `logging` records behind the scenes.\n\n# Installation\n\n```sh\n$ pip install minilog\n```\n',
    'author': 'Jace Browning',
    'author_email': 'jacebrowning@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/minilog',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
