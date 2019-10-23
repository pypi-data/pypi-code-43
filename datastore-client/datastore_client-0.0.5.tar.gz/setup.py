# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['datastore_client']

package_data = \
{'': ['*']}

install_requires = \
['google-cloud-datastore>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'datastore-client',
    'version': '0.0.5',
    'description': 'A simple Google DataStore client',
    'long_description': "# Simple DataStore Client\n\nA simple Google DataStore client that exposes 3 functions on the `DatastoreClient` class.\n\n```python\nclass DatastoreClient:\n    def __init__(self, namespace: str=None, **kwargs) -> None:\n        self.client = Client(namespace=namespace, **kwargs)\n\n    def set_key(\n        self,\n        entity_name: str,\n        key_name: str,\n        **properties: Any,\n    ) -> None:\n        ...\n\n    def get_key(\n        self,\n        entity_name: str,\n        key_name: str,\n    ) -> Optional[Entity]:\n        ...\n\n    def query_entity(\n        self,\n        entity_name: str,\n        *query_filters: Tuple[str, str, Any],\n        projection: List[str]=None,\n        limit: Optional[int]=None,\n    ) -> Iterator:\n        ...\n```\n\n## Examples\n\n### Changing the `namespace`\nYou can set the `namespace` for the client by passing it in to the constructor\n```python\nfrom datastore_client.client import DatastoreClient\n\nclient = DatastoreClient(namespace='namespace_A')\n```\n\nThe following will change the namespace for all subsequent function calls.\n\n```python\nfrom datastore_client.client import DatastoreClient\n\nclient = DatastoreClient()\nclient.client.namespace = 'specific_namespace'\n```\n\n### `set_key`\n\n```python\nfrom datastore_client.client import DatastoreClient\n\nclient = DatastoreClient()\nclient.set_key(\n    entity_name=RECHARGE_NOTES_ENTITY, \n    key_name=note_key, \n    username=username, \n    reference=reference, \n    note=notes,\n)\n```\n\n### `get_key`\n\n```python\nfrom datastore_client.client import DatastoreClient\n\nclient = DatastoreClient()\nclient.get_key(LOGIN_ENTITY, username)\n```\n\n### `query_entity`\n\n```python\nfrom datastore_client.client import DatastoreClient\n\nclient = DatastoreClient()\nproduct_list = list(client.query_entity(\n    PRODUCT_ENTITY,\n    ('network', '=', network_name),\n    ('product_type', '=', product_code),\n    ('bundle_size', '=', denomination),\n    projection=['id'],\n    limit=1,\n))\n\nprint(product_list[0]['id'])\n```\n",
    'author': 'Jethro Muller',
    'author_email': 'git@jethromuller.co.za',
    'url': 'https://github.com/Flickswitch/datastore-client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
