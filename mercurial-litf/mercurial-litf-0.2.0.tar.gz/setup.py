# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['mercurial_litf']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['mercurial-litf = mercurial_litf.cli:main']}

setup_kwargs = {
    'name': 'mercurial-litf',
    'version': '0.2.0',
    'description': 'A litf plugin for the Mercurial test runner',
    'long_description': '# mercurial-litf\n\nA litf compatible plugin for the [Mercurial](https://www.mercurial-scm.org/) test runner.\n\nIt can be used with [Balto: BAlto is a Language independent Test Orchestrator](https://lothiraldan.github.io/balto/).\n\n# Installation\n\n\nYou can install "mercurial-litf" via\n[pip](https://pypi.python.org/pypi/pip/) from\n[PyPI](https://pypi.python.org/pypi):\n\n```\n    $ pip install mercurial-litf\n```\n\n# Configuration\n\nThe mercurial-litf CLI need to find where the Mercurial test-runner is located. It reads the `MERCURIAL_RUN_TESTS_PATH` environment variable in order to do so, please ensure it\'s defined in your environment.\n',
    'author': 'Boris Feld',
    'author_email': 'lothiraldan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://bitbucket.org/lothiraldan/mercurial_litf',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*',
}


setup(**setup_kwargs)
