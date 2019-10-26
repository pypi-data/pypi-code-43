# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['safe_assert']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'safe-assert',
    'version': '0.1.0',
    'description': 'Safe assert for Python that can be used together with optimised mode',
    'long_description': "# safe-assert\n\n[![wemake.services](https://img.shields.io/badge/%20-wemake.services-green.svg?label=%20&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC%2FxhBQAAAAFzUkdCAK7OHOkAAAAbUExURQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP%2F%2F%2F5TvxDIAAAAIdFJOUwAjRA8xXANAL%2Bv0SAAAADNJREFUGNNjYCAIOJjRBdBFWMkVQeGzcHAwksJnAPPZGOGAASzPzAEHEGVsLExQwE7YswCb7AFZSF3bbAAAAABJRU5ErkJggg%3D%3D)](https://wemake.services)\n[![Build Status](https://travis-ci.org/wemake-services/docker-image-size-limit.svg?branch=master)](https://travis-ci.org/sobolevn/safe-assert)\n[![Coverage](https://coveralls.io/repos/github/sobolevn/safe-assert/badge.svg?branch=master)](https://coveralls.io/github/sobolevn/safe-assert?branch=master)\n[![Python Version](https://img.shields.io/pypi/pyversions/safe-assert.svg)](https://pypi.org/project/safe-assert/)\n[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/docker-image-size-limit)\n\nAllows users to write `assert`s that are not stripped away in [optimized mode](https://docs.python.org/3/using/cmdline.html#cmdoption-o).\n\n\n## Features\n\n- Single simple, pythonic, fast, tested, typed, documented function. That's it!\n- Because `safe_assert` is a function, it can be easily composed with other functions\n- Fully typed with annotations and checked with mypy, [PEP561 compatible](https://www.python.org/dev/peps/pep-0561/)\n\n\n## Installation\n\n```bash\npip install safe-assert\n```\n\n\n## Examples\n\nThe usage is identical to `assert` keyword, but a function:\n\n```python\nfrom safe_assert import safe_assert\n\ndef sort_positive_number(numbers: List[int]) -> List[int]:\n    safe_assert(all(num >= 0 for num in numbers), 'found negative')\n    return sorted(numbers)\n```\n\nHow is it different from regular `assert`?\nThe major one is that it would not be stripped away with `-O` flag.\nSo, it still allows to write declarative checks that are safe in production.\n\nThe second one is that you can compose it as any other regular function.\nUseful in conjuction with [`dry-python`](https://github.com/dry-python) projects.\n\n\n## Internals\n\nHow does it work internally?\nIt internally raises [`AssertionError`](https://docs.python.org/3/library/exceptions.html#AssertionError) that is also used by the `assert` keyword itself.\n\nSee [docs](https://github.com/sobolevn/safe-assert/blob/master/safe_assert/__init__.py) to learn more.\n\n\n## License\n\nMIT.\n",
    'author': 'sobolevn',
    'author_email': 'mail@sobolevn.me',
    'url': 'https://github.com/sobolevn/safe-assert',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
