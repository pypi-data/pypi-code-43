# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['bareasgi_graphql_next']

package_data = \
{'': ['*']}

install_requires = \
['bareASGI>=3.0,<4.0', 'bareutils>=3.0,<4.0', 'graphql-core>=3.0.0a0,<4.0.0']

setup_kwargs = {
    'name': 'bareasgi-graphql-next',
    'version': '3.9.1',
    'description': 'GraphQL support for the bareASGI framework',
    'long_description': '# bareASGI-graphql-next\n\nGraphql support for [bareASGI](http://github.com/rob-blackbourn/bareasgi) (read the [documentation](https://bareasgi-graphql-next.readthedocs.io/en/latest/))\n\nThe controller provides a GraphQL GET and POST route, a WebSocket subscription server, and a Graphiql view.\n\n## Installation\n\nInstall from the pie shop.\n\n```bash\npip install bareasgi-graphql-next\n```\n\n## Usage\n\nYou can register the graphql controller with the `add_graphql_next` function.\n\n```python\nfrom bareasgi import Application\nfrom bareasgi_graphql_next import add_graphql_next\nimport graphql\n\n# Get the schema ...\nschema = graphql.GraphQLSchema( ... )\n\nimport uvicorn\n\napp = Application()\nadd_graphql_next(app, schema)\n\nuvicorn.run(app, port=9009)\n\n```\n\n',
    'author': 'Rob Blackbourn',
    'author_email': 'rob.blackbourn@gmail.com',
    'url': 'https://github.com/rob-blackbourn/bareasgi-graphql-next',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
