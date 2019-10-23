# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['benchlingapi', 'benchlingapi.models']

package_data = \
{'': ['*']}

install_requires = \
['bs4>=0.0.1,<0.0.2',
 'inflection>=0.3.1,<0.4.0',
 'marshmallow>=3.2,<4.0',
 'requests>=2.22,<3.0',
 'urlopen>=1.0,<2.0']

setup_kwargs = {
    'name': 'benchlingapi',
    'version': '2.1.3',
    'description': 'An unofficial python wrapper for the Benchling API',
    'long_description': '# BenchlingAPI\n\n[![PyPI version](https://badge.fury.io/py/benchlingapi.svg)](https://badge.fury.io/py/benchlingapi)\n\nThe (unofficial) python API wrapper for Benchling. For more information,\nsee documentation at https://klavinslab.github.io/benchling-api/index.\n\n## Installation\n\n```\npip install benchlingapi -U\n```\n\n## Getting Started\n\nInitialize a session using your Benchling-provided API key:\n\n```python\nfrom benchlingapi import Session\nsession = Session("your_secret_benchling_api_key")\n```\n\nFrom there, you can access various models:\n\n```python\nsession.DNASequence\nsession.AASequence\nsession.Oligo\nsession.Folder\nsession.Project\nsession.Registry\nsession.Translation\nsession.EntitySchema\nsession.Batch\nsession.CustomEntity\n```\n\nFinding models:\n\n```python\n# get one model\ndna = session.DNASequence.one()\n\n# find a specific model by its id\ndna = session.DNASequence.find(\'sdg_4tg23\')\n\n# get the last 50 amino acids\nproteins = session.AASequence.last(50)\n\n# get a registry by name\nregistry = session.Registry.find_by_name("Klavins Lab Registry")\n```\n\nUpdating models:\n\n```python\ndna = session.DNASequence.one()\ndna.name = "My new name"\ndna.bases = "AGGTAGGGTAGGGCCAGAGA"\n\n# update the sequence on the server\ndna.update()\n```\n\nSaving new models:\n\n```python\nfolder = session.Folder.find_by_name("My API Folder")\ndna = session.DNASequence(\n    name = \'my new dna\',\n    bases = \'AGGTAGGATGGCCA\',\n    folder_id = folder.id,\n    is_circular = False\n)\n\n# save the dna to your Benchling account\ndna.save()\n```\n\nRegistering models to your registry:\n\n```python\ndna.set_schema("My DNA Schema")\ndna.register()\n```\n\nSee the documentation for more information: https://klavinslab.github.io/benchling-api/index\n\n## Testing\n\nTesting is done using `pytest`. Tests will create live requests to a Benchling account.\nSince testing is done live, a Benchling account will need to be setup along with testing\ndata.\n\nTo run tests, you must have a Benchling Account with an API key. Tests require a file in\n\'tests/secrets/config.json\' with the following format:\n\n```\n{\n  "credentials": {\n    "api_key": "asdahhjwrthsdfgadfadfgadadsfa"\n  },\n  "sharelinks": [\n    "https://benchling.com/s/seq-asdfadsfaee"\n  ],\n  "project": {\n    "name": "API"\n  },\n  "trash_folder": {\n    "name": "API_Trash"\n  },\n  "inventory_folder": {\n    "name": "API_Inventory"\n  }\n}\n```\n\nOn the Benchling side of things, in the account liked to the `credentials["api_key"]`, you must\nhave a project corresponding to the `project["name"]` value above. Within this project, you should\nhave two folder corresponding to the `trash_folder` and `inventory_folder` values above. Additionally,\nyou should have at least one example of an AminoAcid, DNASequence, CustomEntity, and Oligo stored within\nyour `inventory_folder`. Tests will copy the examples from the `inventory_folder` for downstream tests.\nAfter the tests, conclude, inventory in the `trash_folder` will get archived.\n\n#### Happy Cloning!\n',
    'author': 'Justin Vrana',
    'author_email': 'justin.vrana@gmail.com',
    'url': 'https://www.github.com/klavinslab/benchling-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5.2,<4.0.0',
}


setup(**setup_kwargs)
