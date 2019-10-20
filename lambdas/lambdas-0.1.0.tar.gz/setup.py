# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['lambdas', 'lambdas.contrib', 'lambdas.contrib.mypy']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=3.7,<4.0']

setup_kwargs = {
    'name': 'lambdas',
    'version': '0.1.0',
    'description': 'Typed lambdas that are short and readable',
    'long_description': "[![lambdas logo](https://raw.githubusercontent.com/dry-python/brand/master/logo/lambdas.png)](https://github.com/dry-python/lambdas)\n\n-----\n\n[![Build Status](https://travis-ci.org/dry-python/lambdas.svg?branch=master)](https://travis-ci.org/dry-python/lambdas)\n[![Coverage Status](https://coveralls.io/repos/github/dry-python/lambdas/badge.svg?branch=master)](https://coveralls.io/github/dry-python/lambdas?branch=master)\n[![Documentation Status](https://readthedocs.org/projects/lambdas/badge/?version=latest)](https://lambdas.readthedocs.io/en/latest/?badge=latest)\n[![Python Version](https://img.shields.io/pypi/pyversions/lambdas.svg)](https://pypi.org/project/lambdas/)\n[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide) [![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)\n\n-----\n\nWrite short and fully-typed `lambda`s where you need them.\n\n\n## Features\n\n- Allows to write `lambda`s as `_`\n- Fully typed with annotations and checked with `mypy`, [PEP561 compatible](https://www.python.org/dev/peps/pep-0561/)\n- Has a bunch of helpers for better composition\n- Easy to start: has lots of docs, tests, and tutorials\n\n\n## Installation\n\n```bash\npip install lambdas\n```\n\nWe also recommend to use the same `mypy` settings [we use](https://github.com/wemake-services/wemake-python-styleguide/blob/master/styles/mypy.toml).\n\n\n## Examples\n\nImagine that you need to sort an array of dictionaries like so:\n\n```python\nscores = [\n    {'name': 'Nikita', 'score': 2},\n    {'name': 'Oleg', 'score': 1},\n    {'name': 'Pavel', 'score': 4},\n]\n\nprint(sorted(scores, key=lambda item: item['score']))\n```\n\nAnd it works perfectly fine.\nExcept, that you have to do a lot of typing for such a simple operation.\n\nThat's where `lambdas` helper steps in:\n\n```python\nscores = [\n    {'name': 'Nikita', 'score': 2},\n    {'name': 'Oleg', 'score': 1},\n    {'name': 'Pavel', 'score': 4},\n]\n\nprint(sorted(scores, key=_['score']))\n```\n\nIt might really save you a lot of effort,\nwhen you use a lot of `lambda` functions.\nLike when using [`returns`](https://github.com/dry-python/returns) library.\n\nWork in progress:\n\n- `_.some_attribute` is not supported yet, because we need a complex `mypy` plugin for this\n- `_.method()` is not supported yet for the same reason\n- `TypedDict`s are not tested with `__getitem__`\n- `__getitem__` does not work with list and tuples (collections), only dicts (mappings)\n\nFor now you will have to use regular `lamdba`s in these cases.\n",
    'author': 'sobolevn',
    'author_email': 'mail@sobolevn.me',
    'url': 'https://lambdas.readthedocs.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
