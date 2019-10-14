# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['cachalot']

package_data = \
{'': ['*']}

install_requires = \
['jsonpickle', 'tinydb', 'tinydb-smartcache']

setup_kwargs = {
    'name': 'cachalot',
    'version': '1.3.0',
    'description': 'Minimal persistent memoization cache',
    'long_description': "# Cachalot [![PyPI version](https://badge.fury.io/py/cachalot.svg)](https://badge.fury.io/py/cachalot) [![Pipeline status](https://gitlab.com/radek-sprta/cachalot/badges/master/pipeline.svg)](https://gitlab.com/radek-sprta/cachalot/commits/master) [![Coverage report](https://gitlab.com/radek-sprta/cachalot/badges/master/coverage.svg)](https://gitlab.com/radek-sprta/cachalot/commits/master)\n\nCachalot is a minimal persistent memoization cache. It provides a decorator, that stores function result for future use. Perfect for heavy computations and I/O operation (such as web requests). On backend, it uses TinyDB for storage.\n\n## Features\n- Simple usage via decorator\n- Persistent caching\n- Key expiration\n- Maximum cache size, to prevent bloat\n\n## Installation\nCachalot requires Python 3.5 or newer to run.\n\n**Python package**\n\nYou can easily install Cachalot using pip:\n\n`pip3 install cachalot`\n\n**Manual**\n\nAlternatively, to get the latest development version, you can clone this repository and then manually install it:\n\n```\ngit clone git@gitlab.com:radek-sprta/cachalot.git\ncd cachalot\npython3 setup.py install\n```\n\n## Usage\n```python\nfrom cachalot import Cache\n\n@Cache()\ndef expensive_function():\n    return expensive_calculation()\n```\n\n### Advanced usage\n```python\nfrom cachalot import Cache\n\n@Cache(path='cache.json', timeout=3600, size=5e3, filesize=1e6, retry=True, renew_on_read=True)\ndef expensive_function():\n    return expensive_calculation()\n```\n\n- `path`: Path to the database file. Defaults to .cache.json.\n- `timeout`: How long should the data be cached in seconds. Defaults to 0 (infinite).\n- `size`: Maximum number of keys cached. Defaults to 0 (infinite).\n- `filesize`: Maximum size of database file in bytes. Defaults to 0 (infinite).\n- `retry`: Retry if result is blank. Defaults to False.\n- `renew_on_read`: Renew the entry, i.e refresh the entry timestamp on reads. Defaults to True\n\nFor more information, see [documentation][documentation].\n\n## Contributing\nFor information on how to contribute to the project, please check the [Contributor's Guide][contributing]\n\n## Contact\n[mail@radeksprta.eu](mailto:mail@radeksprta.eu)\n\n[incoming+radek-sprta/cachalot@gitlab.com](incoming+radek-sprta/cachalot@gitlab.com)\n\n## License\nMIT License\n\n## Credits\nThis package was created with [Cookiecutter][cookiecutter] and the [python-cookiecutter][python-cookiecutter] project template. Inspired by [Cashier][cachier]\n\n[cachier]: https://github.com/atmb4u/cashier\n[contributing]: https://gitlab.com/radek-sprta/cachalot/blob/master/CONTRIBUTING.md\n[cookiecutter]: https://github.com/audreyr/cookiecutter\n[documentation]: https://radek-sprta.gitlab.io/cachalot\n[python-cookiecutter]: https://gitlab.com/radek-sprta/python-cookiecutter\n",
    'author': 'Radek Sprta',
    'author_email': 'mail@radeksprta.eu',
    'url': 'https://radek-sprta.gitlab.io/cachalot/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
