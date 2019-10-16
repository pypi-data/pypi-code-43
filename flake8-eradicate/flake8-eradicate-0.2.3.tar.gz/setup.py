# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['flake8_eradicate']
install_requires = \
['attrs>=18.2,<20.0', 'eradicate>=0.2.1,<1.1.0', 'flake8>=3.5,<4.0']

entry_points = \
{'flake8.extension': ['E8 = flake8_eradicate:Checker']}

setup_kwargs = {
    'name': 'flake8-eradicate',
    'version': '0.2.3',
    'description': 'Flake8 plugin to find commented out code',
    'long_description': '# flake8-eradicate\n\n[![wemake.services](https://img.shields.io/badge/-wemake.services-green.svg?label=%20&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC%2FxhBQAAAAFzUkdCAK7OHOkAAAAbUExURQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP%2F%2F%2F5TvxDIAAAAIdFJOUwAjRA8xXANAL%2Bv0SAAAADNJREFUGNNjYCAIOJjRBdBFWMkVQeGzcHAwksJnAPPZGOGAASzPzAEHEGVsLExQwE7YswCb7AFZSF3bbAAAAABJRU5ErkJggg%3D%3D)](https://wemake.services)\n[![Build Status](https://travis-ci.org/sobolevn/flake8-eradicate.svg?branch=master)](https://travis-ci.org/sobolevn/flake8-eradicate)\n[![Coverage](https://coveralls.io/repos/github/sobolevn/flake8-eradicate/badge.svg?branch=master)](https://coveralls.io/github/sobolevn/flake8-eradicate?branch=master) [![Python Version](https://img.shields.io/pypi/pyversions/flake8-eradicate.svg)](https://pypi.org/project/flake8-eradicate/)\n[![PyPI version](https://badge.fury.io/py/flake8-eradicate.svg)](https://pypi.org/project/flake8-eradicate/)\n[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)\n\n`flake8` plugin to find commented out (or so called "dead") code.\n\nThis is quite important for the project in a long run.\nBased on [`eradicate`](https://github.com/myint/eradicate) project.\n\n\n## Installation\n\n```bash\npip install flake8-eradicate\n```\n\nIt is also a valuable part of [`wemake-python-styleguide`](https://github.com/wemake-services/wemake-python-styleguide).\n\n\n## Usage\n\nRun your `flake8` checker [as usual](http://flake8.pycqa.org/en/latest/user/invocation.html).\nCommented code should raise an error.\n\nExample:\n\n```bash\nflake8 your_module.py\n```\n\n\n## Options\n\n- `--eradicate-aggressive` to enable aggressive mode from `eradicate`, can lead to false positives\n\n\n## Error codes\n\n| Error code |        Description       |\n|:----------:|:------------------------:|\n|    E800    | Found commented out code |\n\n\n## Output example\n\nHere\'s how output looks like (we are using [`wemake` formatter](https://wemake-python-stylegui.de/en/latest/pages/formatter.html)):\n\n![flake8-eradicate output](https://raw.githubusercontent.com/sobolevn/flake8-eradicate/master/eradicate.png)\n\n\n## License\n\nMIT.\n',
    'author': 'Nikita Sobolev',
    'author_email': 'mail@sobolevn.me',
    'url': 'https://github.com/sobolevn/flake8-eradicate',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
