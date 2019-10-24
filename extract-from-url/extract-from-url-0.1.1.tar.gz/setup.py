# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['extract_from_url']

package_data = \
{'': ['*']}

install_requires = \
['libarchive-c>=2.9,<3.0', 'tqdm>=4.36.1,<5.0.0']

setup_kwargs = {
    'name': 'extract-from-url',
    'version': '0.1.1',
    'description': 'Download and extract files on-the-fly (ZIP files too)',
    'long_description': 'Description\n===========\n\nTake advantage of `libarchive <https://libarchive.org/>`_ to download and extract files without having to store the archive first. Works with ZIP files too!\n\nDependencies\n============\n\n1. `libarchive-c <https://pypi.org/project/libarchive-c/>`_ which requires ``libarchive-devel`` or ``libarchive-dev`` to be built\n2. `tqdm <https://pypi.org/project/tqdm/>`_ for progress bars\n\nYou can use `poetry <https://poetry.eustace.io/>`_ or `pip <https://pip.pypa.io/>`_ to install the dependencies.\n\nUsage\n=====\n\nPlease see ``cli.py --help``\n',
    'author': 'Francesco Frassinelli',
    'author_email': 'francesco.frassinelli@nina.no',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/frafra/extract-from-url',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
