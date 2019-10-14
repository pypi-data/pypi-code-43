# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['repka']

package_data = \
{'': ['*']}

install_requires = \
['aiopg>=0.16.0,<0.17.0', 'pydantic>=0.31,<0.32', 'sqlalchemy>=1.3,<2.0']

setup_kwargs = {
    'name': 'repka',
    'version': '0.7.0',
    'description': 'Python repository pattern implementation',
    'long_description': '# repka\n\nPython repository pattern implementation\n\n## Installation\n\nVia pip:\n\n```\npip install repka\n```\n\nVia poetry:\n\n```\npoetry add repka\n```\n\n\n## Usage\n\n```python\nfrom typing import Any\nimport sqlalchemy as sa\nfrom aiopg.sa import create_engine\nfrom repka.api import BaseRepository, IdModel\n\n# Define SA table\nmetadata = sa.MetaData()\ntransactions_table = sa.Table(\n    "transactions",\n    metadata,\n    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),\n    ...\n)\n\n# Define pydantic model\nclass Transaction(IdModel):\n    ...\n\n\n# Define repository\nclass TransactionRepo(BaseRepository):\n    table = transactions_table\n\n    def deserialize(self, **kwargs: Any) -> Transaction:\n        return Transaction(**kwargs)\n\n# Create SA connection\nconnection_params = dict(user=\'aiopg\', database=\'aiopg\', host=\'127.0.0.1\', password=\'passwd\')\nasync with create_engine(**connection_params) as engine:\n    async with engine.acquire() as conn:\n        # Instantiate repository \n        repo = TransactionRepo(conn)\n        # Now you can use the repo\n        # Here we select first matching row from table and convert it to model\n        transaction = await repo.first(transactions_table.c.id == 1)\n\n```\n\n\n## Tests \n\nTo run tests:\n\n1. Setup [database url](https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls) via `DATABASE_URL` environment variable  \n\n**WARNING:** Every test run will drop all tables from db\n\n2. Run tests via `pytest`\n\n## Contribution\n\n1. Create fork/branch for new feature/fix/whatever\n\n2. Install pre-commit hooks: `pre-commit install` (for manual pre-commit run use`pre-commit run -a`)\n\n3. When you done create pull request and wait for approval\n',
    'author': 'potykion',
    'author_email': 'potykion@gmail.com',
    'url': 'https://github.com/potykion/repka',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
