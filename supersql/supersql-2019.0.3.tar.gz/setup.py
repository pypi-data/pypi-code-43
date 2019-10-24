# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['supersql', 'supersql.containers']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['supersql = supersql:main']}

setup_kwargs = {
    'name': 'supersql',
    'version': '2019.0.3',
    'description': 'Thin wrapper on top of SQL that enables you write SQL code in python easily',
    'long_description': "Supersql Library\n================\n\nSupersql is a `very thin wrapper` on top of SQL that enables you write SQL code in python easily.\n\n&nbsp;\n\n## Why?\nLet's be honest, writing sql templates using string formatting is really painful.\nSQLAlchemy is great, but sometimes an ORM is not what you need, and whilst the new\n`f strings` in python solve a lot of problems, complex SQL templating is not of\nthem.\n\nSupersql makes it super simple to connect to and start querying a database in python.\n\nLet the code do the explanation:\n```py\n\nfrom supersql import Connection, Query\n\n\nconnection = Connection('postgres:localhost:5432', user='postgres', password='postgres')\n\nquery = Query()\n\n\nresults = query.SELECT(\n        'first_name', 'last_name', 'email'\n    ).FROM(\n        'employees'\n    ).WHERE('email', equals='someone@example.com').run()\n\n\nfor result in results:\n    print(result)\n\n```\n\n&nbsp;\n\nToo many magic literals? I agree. Let's try that again with a Schema\n\n```py\n# Schemas help you remove all those magic literals e.g. 'email' string typed twice\n# from your code\nfrom supersql import Schema, String, Date, Integer\n\nclass Employee(Schema):\n    __pk__ = ('email', 'identifier')\n\n    identifier = UUID(pg='uuid_version1', mysql=None)  # mysql included for examples sake\n    email = String(required=True, unique=None, length=25)\n    age = Integer()\n    first_name = String(required=True)\n    last_name = String(25)\n    created_on = Date()\n\n\n# Now lets try again\nemp = Employee()\nresults = query.SELECT(\n    emp.first_name, emp.last_name, emp.email\n).FROM(\n    emp\n).WHERE(\n    emp.email, equals='someone@example.com'\n).run()\n```\n\n\n&nbsp;\n\n# NOTE: Still Very Much In Development -- Expected Launch Date (November 11 2019)\n\nSupersql is not installable until launch\n",
    'author': 'Raymond Ortserga',
    'author_email': 'codesage@live.com',
    'url': 'https://github.com/rayattack/supersql',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
