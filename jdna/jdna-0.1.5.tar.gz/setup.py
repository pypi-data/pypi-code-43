# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['jdna', 'jdna.regions']

package_data = \
{'': ['*']}

install_requires = \
['biopython>=1.73,<2.0',
 'colorama>=0.4.1,<0.5.0',
 'networkx>=2.3,<3.0',
 'primer3-py>=0.6.0,<0.7.0',
 'webcolors>=1.9,<2.0']

setup_kwargs = {
    'name': 'jdna',
    'version': '0.1.5',
    'description': '',
    'long_description': '# jdna\n\nA Python DNA sequence editor that represents sequences as a linked list.\nIt includes basic molecular reaction simulations (primer annealing, pcr, dna assembly),\n basic format conversion, and a viewer class.\n\n[Documentation is here](https://jvrana.github.io/jdna/index)\n\n![example.png](./docsrc/_static/viewer.png)\n',
    'author': 'Justin Vrana',
    'author_email': 'justin.vrana@gmail.com',
    'url': 'https://github.com/jvrana/jdna',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
