# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['burpless']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'lark-parser>=0.7.2,<0.8.0']

entry_points = \
{'console_scripts': ['burpless = burpless.Cli:Cli.main',
                     "include = ['grammar/grammar.ebnf']"]}

setup_kwargs = {
    'name': 'burpless',
    'version': '0.1.1',
    'description': 'A gherkin parser that uses LALR instead of regex for parsing',
    'long_description': None,
    'author': 'Jacopo Cascioli',
    'author_email': 'jacopo@jacopocascioli.com',
    'url': 'https://github.com/strangemachines/burpless',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
