# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['commitment']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'commitment',
    'version': '2.0.2',
    'description': 'An incomplete Python 3 wrapper for the GitHub API',
    'long_description': '# commitment\n\n[![Build Status](https://travis-ci.org/chris48s/commitment.svg?branch=master)](https://travis-ci.org/chris48s/commitment)\n[![Coverage Status](https://coveralls.io/repos/github/chris48s/commitment/badge.svg?branch=master)](https://coveralls.io/github/chris48s/commitment?branch=master)\n![PyPI Version](https://img.shields.io/pypi/v/commitment.svg)\n![License](https://img.shields.io/pypi/l/commitment.svg)\n![Python Support](https://img.shields.io/pypi/pyversions/commitment.svg)\n![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)\n\nAn incomplete Python 3 wrapper for the [GitHub API](https://developer.github.com/v3/).\n\nNote this project does not aim to provide a complete abstraction over the GitHub API - just a few high-level convenience methods for pushing data to a GitHub repo.\n\n## Installation\n\n`pip install commitment`\n\n## Usage\n\nGenerate a GitHub API key: https://github.com/settings/tokens\n\n```python\nfrom commitment import GitHubCredentials, GitHubClient\n\ncredentials = GitHubCredentials(\n    repo="myuser/somerepo",\n    name="myuser",\n    email="someone@example.com",\n    api_key="f00b42",\n)\n\nclient = GitHubClient(credentials)\n\nclient.create_branch(\'my_new_branch\', base_branch=\'master\')\nclient.push_file(\'Hello World!\', \'directory/filename.txt\', \'my commit message\', branch=\'my_new_branch\')\nclient.open_pull_request(\'my_new_branch\', \'title\', \'body\', base_branch=\'master\')\n```\n',
    'author': 'chris48s',
    'author_email': None,
    'url': 'https://github.com/chris48s/commitment',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
