# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['verchew', 'verchew.tests']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['verchew = verchew.script:main']}

setup_kwargs = {
    'name': 'verchew',
    'version': '2.0.1',
    'description': 'System dependency version checker.',
    'long_description': "# Overview\n\n> ...chews through your system dependencies, spitting out incompatible versions.\n\nWhen onboarding new team members, ensuring their computer has everything needed to work on the project can be painful. Verchew is a command-line program and embeddable Python script to check the versions of your project's system dependencies. Its only external dependency is any Python interpreter, which should already be installed on macOS and most Linux-based operating systems.\n\n[![Unix Build Status](https://img.shields.io/travis/jacebrowning/verchew/develop.svg?label=unix)](https://travis-ci.org/jacebrowning/verchew)\n[![Windows Build Status](https://img.shields.io/appveyor/ci/jacebrowning/verchew/develop.svg?label=windows)](https://ci.appveyor.com/project/jacebrowning/verchew)\n[![Coverage Status](https://img.shields.io/coveralls/jacebrowning/verchew/develop.svg)](https://coveralls.io/r/jacebrowning/verchew)\n[![Scrutinizer Code Quality](https://img.shields.io/scrutinizer/g/jacebrowning/verchew.svg)](https://scrutinizer-ci.com/g/jacebrowning/verchew/?branch=develop)\n[![PyPI Version](https://img.shields.io/pypi/v/verchew.svg)](https://pypi.python.org/pypi/verchew)\n[![PyPI License](https://img.shields.io/pypi/l/verchew.svg)](https://pypi.org/project/verchew)\n\n# Setup\n\n## Requirements\n\n* Python 2.7+ or Python 3.3+\n\n## Installation\n\nInstall `verchew` globally with pip:\n\n```text\n$ pip install verchew\n```\n\nor embedded the script in your project using [this guide](https://verchew.readthedocs.io/en/latest/cli/vendoring/).\n\n# Usage\n\nRun `verchew --init` to generate a sample configuration file.\n\nUpdate this file (`verchew.ini`) to include your project's system dependencies:\n\n```ini\n[Working Program]\n\ncli = working-program\nversion = 1.2\n\n[Newer Working Program]\n\ncli = working-program\nversion =  4.1 || 4.2\nmessage = Version 4.x is required to get the special features.\n\n[Broken Program]\n\ncli = broken-program\nversion = 1.2.3\n\n[Optional Missing Program]\n\ncli = missing-program\nversion = 1.2.3\noptional = true\n\n[Missing Program]\n\ncli = missing-program\nversion = 1.2.3\n```\n\nRun `verchew` to see if you have the expected versions installed:\n\n```text\n$ verchew\n\nChecking for Working Program...\n\n$ working-program --version\n1.2.3\n✔ MATCHED: 1.2\n\nChecking for Newer Working Program...\n\n$ working-program --version\n1.2.3\n✘ EXPECTED: 4.1 || 4.2\n⭑ MESSAGE: Version 4.x is required to get the special features.\n\nChecking for Broken Program...\n\n$ broken-program --version\nAn error occurred.\n✘ EXPECTED: 1.2.3\n\nChecking for Optional Missing Program...\n\n$ missing-program --version\nsh: command not found: missing-program\n⚠ EXPECTED: 1.2.3\n\nChecking for Missing Program...\n\n$ missing-program --version\nsh: command not found: missing-program\n✘ EXPECTED: 1.2.3\n\nResults: ✔ ✘ ✘ ⚠ ✘\n```\n",
    'author': 'Jace Browning',
    'author_email': 'jacebrowning@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/verchew',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
