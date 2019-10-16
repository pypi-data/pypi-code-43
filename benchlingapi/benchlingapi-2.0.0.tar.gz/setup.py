# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['benchlingapi', 'benchlingapi.models']

package_data = \
{'': ['*']}

install_requires = \
['bs4>=0.0.1,<0.0.2',
 'inflection>=0.3.1,<0.4.0',
 'marshmallow==3.0.0rc1',
 'requests>=2.22,<3.0',
 'urlopen>=1.0,<2.0']

setup_kwargs = {
    'name': 'benchlingapi',
    'version': '2.0.0',
    'description': 'An unofficial python wrapper for the Benchling API',
    'long_description': '# BenchlingAPI\n\nThe (unofficial) python API wrapper for Benchling.\n\n## Installation\n\n```\npip install benchlingapi -U\n```\n\n## Getting Started\n\n`api = Session("your_secret_benchling_api_key")`\n\n`api.DNASequence()`\n\n`api.AASequence()`\n\n`api.CustomEntity()`\n\n`api.Oligo()`\n\n`api.Registry.one()`\n\n`api.DNASequence.one()`\n\n`api.DNASequence.last(50)`\n\n`api.Folder.find_by_name("MyFolderName")`\n\n```\ndna.set_schema("My DNA Schema")\ndna.register()\n```\n\n## Testing\n\nTesting is done using `pytest`. Tests will create live requests to a Benchling account.\nSince testing is done live, a Benchling account will need to be setup along with testing\ndata.\n\nTo run tests, you must have a Benchling Account with an API key. Tests require a file in\n\'tests/secrets/config.json\' with the following format:\n\n```\n{\n  "credentials": {\n    "api_key": "asdahhjwrthsdfgadfadfgadadsfa"\n  },\n  "sharelinks": [\n    "https://benchling.com/s/seq-asdfadsfaee"\n  ],\n  "project": {\n    "name": "API"\n  },\n  "trash_folder": {\n    "name": "API_Trash"\n  },\n  "inventory_folder": {\n    "name": "API_Inventory"\n  }\n}\n```\n\nOn the Benchling side of things, in the account liked to the `credentials["api_key"]`, you must\nhave a project corresponding to the `project["name"]` value above. Within this project, you should\nhave two folder corresponding to the `trash_folder` and `inventory_folder` values above. Additionally,\nyou should have at least one example of an AminoAcid, DNASequence, CustomEntity, and Oligo stored within\nyour `inventory_folder`. Tests will copy the examples from the `inventory_folder` for downstream tests.\nAfter the tests, conclude, inventory in the `trash_folder` will get archived.\n\n#### Happy Cloning!',
    'author': 'Justin Vrana',
    'author_email': 'justin.vrana@gmail.com',
    'url': 'https://www.github.com/klavinslab/benchling-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
