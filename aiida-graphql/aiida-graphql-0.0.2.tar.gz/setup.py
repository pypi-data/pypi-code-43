# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiida_graphql']

package_data = \
{'': ['*'], 'aiida_graphql': ['api/*']}

install_requires = \
['aiida>=1.0.0b6,<2.0.0', 'strawberry-graphql>=0.16.7,<0.17.0']

setup_kwargs = {
    'name': 'aiida-graphql',
    'version': '0.0.2',
    'description': 'Strawberry-based GraphQL API Server for AiiDA',
    'long_description': '# aiida-graphql\n\n[![Build Status](https://travis-ci.com/dev-zero/aiida-graphql.svg?branch=develop)](https://travis-ci.com/dev-zero/aiida-graphql) [![codecov](https://codecov.io/gh/dev-zero/aiida-graphql/branch/develop/graph/badge.svg)](https://codecov.io/gh/dev-zero/aiida-graphql) [![PyPI](https://img.shields.io/pypi/pyversions/aiida-graphql)](https://pypi.org/project/aiida-graphql/)\n\nStrawberry-based GraphQL Server for AiiDA\n\nWhy GraphQL when there is already the REST API? See https://www.howtographql.com/basics/1-graphql-is-the-better-rest/\n... a lot of possible optimizations and fits the graph-based structure of the AiiDA DB a lot better than a REST API.\n\n## Requirements\n\n* Python 3.7+\n* https://pypi.org/project/strawberry-graphql/ 0.16.7+\n* https://pypi.org/project/aiida-core/ 1.0.0b6+\n\nFor development: https://poetry.eustace.io/\n\nWhy Strawberry for GraphQL? It uses graphql-core v3 (while graphene is still stuck with v2), uses typings and dataclasses for both validation and schema generation. And it uses modern Python to write the schema, in comparison to the [schema-first approach](https://ariadnegraphql.org/).\n\nWhy Python 3.7+? It\'s the future, and for Strawberry. In fact, were it not for a bug in `uvloop` this would be Python 3.8+ (for the walrus operator). And given the timeline these projects are running for, we\'ll probably see Python 3.9 until people effectively start using it.\n\nWhy Poetry? I wanted to get away from `setuptools` and used Poetry already in a [different project](https://github.com/dev-zero/cp2k-input-tools) and liked the virtualenv integration.\n\n# Usage\n\n## Development\n\nInstalling the dependencies:\n\n```bash\ngit clone https://github.com/dev-zero/aiida-graphql.git\ncd aiida-graphql\n\n# for poetry installation use the official documentation\npoetry install\n```\n\nTo run the development server:\n\n```console\n$ poetry run strawberry server aiida_graphql.schema\n```\n\nthen visit http://localhost:8000/graphql with your browser.\n\nExample query:\n\n```graphql\n{\n  computers {\n    uuid\n    name\n    description\n    schedulerType\n    transportType\n  }\n}\n```\n\n![Query Screenshot](docs/screenshot.png?raw=true "Query Screenshot")\n\n\n# Available fields\n\n* node\n* calculation\n* computer\n* user\n* singlefile\n* gaussian_basissets (only if the [aiida-gaussian-datatypes](https://github.com/dev-zero/aiida-gaussian-datatypes) is installed)\n\nDocumentation and schema are embedded in the development server.\n',
    'author': 'Tiziano Müller',
    'author_email': 'tiziano.mueller@chem.uzh.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dev-zero/aiida-graphql',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
