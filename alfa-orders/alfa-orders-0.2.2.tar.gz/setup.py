# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['alfa_orders', 'alfa_orders.loaders']

package_data = \
{'': ['*']}

install_requires = \
['more-itertools>=7.2,<8.0',
 'requests>=2.22,<3.0',
 'typing-extensions>=3.7,<4.0']

setup_kwargs = {
    'name': 'alfa-orders',
    'version': '0.2.2',
    'description': 'Lib for loading AlfaBank orders',
    'long_description': '# alfa-orders\n\nLib for loading AlfaBank orders from https://engine.paymentgate.ru\n\nUsage:\n\n```python\nimport datetime as dt\nfrom alfa_orders.api import AlfaService\n\nusername, password = ("**********", "**********")\nservice = AlfaService(username, password)\n\n# from_date, to_date should be in UTC+3\nfrom_date, to_date = dt.datetime(2019, 9, 1), dt.datetime(2019, 10, 1)\ntransactions = list(service.get_transactions(from_date, to_date))\nrefunds = list(service.get_refunds(from_date, to_date))\n```\n',
    'author': 'potykion',
    'author_email': 'potykion@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
