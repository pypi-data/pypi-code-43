# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['beancount_n26']

package_data = \
{'': ['*']}

install_requires = \
['beancount>=2.2,<3.0']

setup_kwargs = {
    'name': 'beancount-n26',
    'version': '0.1.0',
    'description': 'Beancount Importer for N26 CSV exports',
    'long_description': "Beancount N26 Importer\n======================\n\n.. image:: https://github.com/siddhantgoel/beancount-n26/workflows/beancount-n26/badge.svg\n    :target: https://github.com/siddhantgoel/beancount-n26/workflows/beancount-n26/badge.svg\n\n.. image:: https://img.shields.io/pypi/v/beancount-n26.svg\n    :target: https://pypi.python.org/pypi/beancount-n26\n\n.. image:: https://img.shields.io/pypi/pyversions/beancount-n26.svg\n    :target: https://pypi.python.org/pypi/beancount-n26\n\n:code:`beancount-n26` provides an Importer for converting CSV exports of N26_\naccount summaries to the Beancount_ format.\n\nInstallation\n------------\n\n.. code-block:: bash\n\n    $ pip install beancount-n26\n\nIn case you prefer installing from the Github repository, please note that\n:code:`master` is the development branch so :code:`stable` is what you should be\ninstalling from.\n\nUsage\n-----\n\n.. code-block:: python\n\n    from beancount_n26 import N26Importer\n\n    CONFIG = [\n        N26Importer(\n            IBAN_NUMBER,\n            'Assets:N26',\n            language='en',\n            file_encoding='utf-8',\n        ),\n    ]\n\nContributing\n------------\n\nContributions are most welcome!\n\nPlease make sure you have Python 3.6+ and Poetry_ installed.\n\n1. Git clone the repository -\n   :code:`git clone https://github.com/siddhantgoel/beancount-n26`\n\n2. Install the packages required for development -\n   :code:`poetry install`\n\n3. That's basically it. You should now be able to run the test suite -\n   :code:`poetry run py.test`.\n\n.. _Beancount: http://furius.ca/beancount/\n.. _N26: https://n26.com/\n.. _Poetry: https://poetry.eustace.io/\n",
    'author': 'Siddhant Goel',
    'author_email': 'me@sgoel.org',
    'url': 'https://github.com/siddhantgoel/beancount-n26',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
