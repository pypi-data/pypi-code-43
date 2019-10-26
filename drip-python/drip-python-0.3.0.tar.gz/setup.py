# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['drip', 'drip.api']

package_data = \
{'': ['*']}

install_requires = \
['requests-toolbelt>=0.9.1,<0.10.0', 'requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'drip-python',
    'version': '0.3.0',
    'description': "Python wrapper for Drip's REST API",
    'long_description': '# drip-python [![Coverage Status](https://coveralls.io/repos/github/Ishamyyl/drip-python/badge.svg?branch=master)](https://coveralls.io/github/Ishamyyl/drip-python?branch=master) [![CircleCI](https://circleci.com/gh/Ishamyyl/drip-python.svg?style=svg)](https://circleci.com/gh/Ishamyyl/drip-python)\nPython wrapper for the Drip REST API at [developer.drip.com](https://developer.drip.com)\n\n----\n# Installation\n\n```sh\npip install drip-python\n```\n\n# Usage\n\nInitialize the client\n\n```py\n>>> from drip import Client\n>>> d = Client(API_TOKEN, ACCOUNT_ID)\n```\n\nUse the client\'s methods\n\n```py\n>>> d.fetch_user()\n{\'email\': \'ross.hodapp@drip.com\', \'name\': \'Ross Hodapp\', \'time_zone\': \'America/Chicago\'}\n```\n\n# Main Concepts\n\nBe sure to check out [the Wiki](https://github.com/Ishamyyl/drip-python/wiki)!\n\n## 1. Additional Options\n\nBeyond the required arguments, any additional keyword arguments will be added to the call as well. Check the docs for what\'s available.\n\n```py\n>>> cfs = {\'first_name\': \'Ross\'}\n>>> d.create_or_update_subscriber(\'ross.hodapp@drip.com\', custom_fields=cfs)\n{\'email\': \'ross.hodapp+test@drip.com\', \'custom_fields\': {\'first_name\': \'Ross\'}, ... }\n```\n\n## 2. Unpacking the response\n\nThe Drip REST API often returns extra data along side the results you\'re asking for.\n\nThe Client takes care of unpacking that data for you, returning lists, dictionaries, or strings as necessary. If the response doesn\'t have a body, result will return `True` or `False` if the call was [successful or not](http://docs.python-requests.org/en/master/user/quickstart/#response-status-codes).\n\nIf you\'d like the raw [response](http://docs.python-requests.org/en/master/user/quickstart/#response-content), pass the keyward argument `marshall=False` to the method call.\n\n```py\n>>> d.fetch_user(marshall=False)\n<Response [200]>\n```\n\n## 3. Pagination\n\nMost calls that return a list are paginated. By default, the Client automatically gets the maximum amount of objects per page and automatically gets all available pages.\n\nUse the `page` and `per_page` keyword arguments. If a valid `page` is passed to the function, then this will fetch that page only (or the single Response if not `marshall`ed per above).\n\nOtherwise-- that is, if `page` is 0 (default) or negative-- then this will fetch the entire collection and return the full list. This will ignore the `per_page` keyword argument and use `1000` for maximum efficiency.\n\nCurrently, I won\'t support getting all pages of 1 object per page for example, since I don\'t see a valid use-case for this.\n\nThis means essentially that `per_page` only makes sense when asking for a specific \'page\'.\nThis also means that you can only `marshall` a specific `page` (this may change in the future).\n\nAnyway, the default case will be what you want most of the time, so don\'t worry about this too much.\n\n```py\n>>> all_subscribers = d.subscribers()\n>>> len(all_subscribers)\n1234\n\n>>> first_page = d.subscribers(page=1)\n>>> len(first_page)\n100\n\n>>> last_page = d.subscribers(page=13)\n>>> len(last_page)\n34\n\n>>> big_first_page = d.subscribers(page=1, per_page=1000)\n>>> len(big_first_page)\n1000\n\n>>> big_last_page = d.subscribers(page=2, per_page=1000)\n>>> len(big_last_page)\n234\n\n>>> marshall_without_page = d.subscribers(marshall=False)\n>>> len(marshall_without_a_page)\n1234\n\n>>> marshall_with_page = d.subscribers(page=1, marshall=False)\n>>> marshall_with_page\n<Response [200]>\n```\n\n# FAQ\n\n# Status - v0.3.0 Beta\nWhile devotedly and enthusiastically maintained, this is an un-official side-project and Drip Support is unable to fix issues you run into. Create an Issue on GitHub here instead. Thanks!\n\nPurpose\n\n- [x] Full API coverage, including "v3" Shopper Activity and future endpoints\n- [x] Full unittest code coverage\n- [x] Every endpoint tested live\n- [x] Documentation ~~(readthedocs? github wiki?)~~ wiki!\n- [ ] Web framework support, namely Django and [Responder](https://python-responder.org/en/latest/)\n- [ ] NoSQL utilities\n- [X] ~~AsyncIO support~~ Basically needs a differend repo?\n\n# Changelog\n\n### `v0.3.0`\n\n* Repostiry updates\n\n### `v0.1.4`\n\n* Added raising Errors for when the HTTP call is successful but the API returned that there were errors\n\n### `v0.1.3`\n\n* Added Product support for the Shopper Activity API! Check that out here: [Product Activity](https://developer.drip.com/?shell#product-activity)\n',
    'author': 'Ross Hodapp',
    'author_email': 'ross.hodapp@drip.com',
    'url': 'https://developer.drip.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
