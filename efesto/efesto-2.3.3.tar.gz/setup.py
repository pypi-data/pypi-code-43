# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['efesto',
 'efesto.exceptions',
 'efesto.handlers',
 'efesto.middlewares',
 'efesto.models']

package_data = \
{'': ['*']}

install_requires = \
['bassoon>=1.0,<1.1',
 'click>=7.0,<7.1',
 'falcon-cors>=1.1.7,<1.2.0',
 'falcon>=2.0,<2.1',
 'loguru>=0.3,<0.4',
 'msgpack>=0.6,<0.7',
 'peewee>=3.9,<3.10',
 'psycopg2-binary>=2.7,<2.8',
 'pyjwt>=1.6.4,<1.7.0',
 'python-rapidjson>=0.6,<0.7',
 'ruamel.yaml>=0.15,<0.16']

entry_points = \
{'console_scripts': ['efesto = efesto.Cli:Cli.main']}

setup_kwargs = {
    'name': 'efesto',
    'version': '2.3.3',
    'description': 'RESTful (micro)server that can generate an API in minutes.',
    'long_description': '# Efesto\n\n[![Pypi](https://img.shields.io/pypi/v/efesto.svg?maxAge=600&style=for-the-badge)](https://pypi.python.org/pypi/efesto)\n[![Travis build](https://img.shields.io/travis/strangemachines/efesto.svg?maxAge=600&style=for-the-badge)](https://travis-ci.org/strangemachines/efesto)\n[![Codacy grade](https://img.shields.io/codacy/grade/9a18a3f98f654fef8b6ff86e93f31b56.svg?style=for-the-badge)](https://app.codacy.com/app/strangemachines/efesto)\n[![Codacy coverage](https://img.shields.io/codacy/coverage/9a18a3f98f654fef8b6ff86e93f31b56.svg?style=for-the-badge)](https://app.codacy.com/app/strangemachines/efesto)\n[![Docs](https://img.shields.io/badge/docs-docs-brightgreen.svg?style=for-the-badge&cacheSeconds=3600)](https://efesto.strangemachines.io)\n\nA micro REST API meant to be used almost out of the box with other\nmicroservices.\n\nIt kickstarts you by providing a simple way to build a backend and expose it.\nEfesto uses PostgreSQL and JWTs for authentication.\n\nEfesto follows the UNIX principle of doing one thing and well, leaving you the\nfreedom of choice about other components (authentication, caching, rate-limiting,\nload balancer).\n\n## Installing\nInstall efesto, possibly in a virtual environment:\n\n```sh\npip install efesto\n```\n\nCreate a postgresql database and export the database url:\n\n```sh\nexport DB_URL=postgres://postgres:postgres@localhost:5432/efesto\n```\n\nExport the jwt secret:\n\n```sh\nexport JWT_SECRET=secret\n```\n\nPopulate the db:\n\n```sh\nefesto install\n```\n\nCreate an admin:\n\n```sh\nefesto create users tofu --superuser\n```\n\nNow you can start efesto, with either uwsgi or gunicorn:\n\n```sh\ngunicorn "efesto.App:App.run()"\n```\n\nEfesto should now be running:\n\n\n```sh\ncurl http://localhost:8000/version\n```\n\nRead the complete [documentation](http://efesto.strangemachines.io) to find out more.\n\n## Docker\n\nDocker images are available in the hub:\n\n- `strangemachines/efesto:latest`\n- `strangemachines/efesto:2.3`\n- `strangemachines/efesto:2.2`\n- `strangemachines/efesto:2.1`\n\n## Performance\n\nEfesto performs at about 200 requests/second on a small digital ocean\ndroplet, for requests that include JWT authentication, fetching data and\nprinting out JSON.\n\nYou have seen 100k requests benchmarks, but don\'t be fooled:\nmost benchmarks from authors are made so that their package comes to the top\nand do not reflect real conditions.\n',
    'author': 'Jacopo Cascioli',
    'author_email': 'jacopo@jacopocascioli.com',
    'url': 'https://github.com/strangemachines/efesto',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
