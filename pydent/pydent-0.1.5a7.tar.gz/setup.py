# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pydent',
 'pydent.marshaller',
 'pydent.models',
 'pydent.planner',
 'pydent.utils',
 'pydent.utils.loggable']

package_data = \
{'': ['*']}

install_requires = \
['colorlog>=4.0,<5.0',
 'inflection>=0.3.1,<0.4.0',
 'nest-asyncio>=1.0,<2.0',
 'networkx>=2.3,<3.0',
 'pandas>=0.24.2,<0.25.0',
 'requests>=2.22,<3.0',
 'tqdm>=4.32,<5.0']

setup_kwargs = {
    'name': 'pydent',
    'version': '0.1.5a7',
    'description': "Aquarium's Python API for planning, executing, and analyzing scientific experiments.",
    'long_description': '# Trident: Aquarium API Scripting\n\n[![CircleCI](https://circleci.com/gh/klavinslab/trident/tree/master.svg?style=svg&circle-token=88677c59698d55a127a080cba9ca025cf8072f6c)](https://circleci.com/gh/klavinslab/trident/tree/master)\n[![PyPI version](https://badge.fury.io/py/pydent.svg)](https://badge.fury.io/py/pydent)\n\nTrident is the python API scripting for Aquarium.\n\n## Documentation\n\n[API documentation can be found here at klavinslab.org/trident](http://www.klavinslab.org/trident)\n\n## Requirements\n\n* Python > 3.4\n* An Aquarium login\n\n## Quick installation\n\nPydent can be installed using `pip3`.\n\n```\n    pip3 install pydent\n```\n\nor upgraded using\n\n```\n    pip3 install pydent --upgrade\n```\n\n## Basic Usage\n\n### Logging in\n\n```python\nfrom pydent import AqSession\n\n# open a session\nmysession = AqSession("username", "password", "www.aquarium_nursery.url")\n\n# find a user\nu = mysession.User.find(1)\n\n# print the user data\nprint(u)\n```\n\n### Models\n\n```python\nprint(mysession.models)\n```\n\n#### Finding models\n\n* By name: `nursery.SampleType.find_by_name("Primer")`\n\n* By ID: `nursery.SampleType.find(1)`\n\n* By property: `nursery.SampleType.where({\'name\': \'Primer\'})`\n\n* All models: `nursery.SampleType.all()`\n\n#### Getting nested data\n\n```python\n# samples are linked to sample_type\nprimer_type = mysession.SampleType.find_by_name("Primer")\nprimers = primer_type.samples\n\n# and sample type is linked to sample\np = primers[0]\nprint(p.sample_type)\n```\n\n#### Available nested relationships\n\n```python\nprimer_type = mysession.SampleType.find(1)\nprint(primer_type.relationships)\n```\n\n\n## Contributors:\n\nvia `git fame -wMC --excl \'.(png|gif|enc)$\'`\n\nTotal commits: 965\nTotal ctimes: 1348\nTotal files: 477\nTotal loc: 100924\n| Author           |   loc |   coms |   fils |  distribution   |\n|:-----------------|------:|-------:|-------:|:----------------|\n| Justin Vrana     | 88573 |    295 |    275 | 87.8/30.6/57.7  |\n| jvrana           | 12187 |    499 |    163 | 12.1/51.7/34.2  |\n| Ben Keller       |   141 |    118 |     34 | 0.1/12.2/ 7.1   |\n| Eric Klavins     |    20 |     47 |      3 | 0.0/ 4.9/ 0.6   |\n| Ubuntu           |     2 |      3 |      1 | 0.0/ 0.3/ 0.2   |\n| gasnew           |     1 |      1 |      1 | 0.0/ 0.1/ 0.2   |\n| Devin Strickland |     0 |      2 |      0 | 0.0/ 0.2/ 0.0   |',
    'author': 'jvrana',
    'author_email': 'justin.vrana@gmail.com',
    'url': 'https://www.github.com/klavinslab/trident',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
