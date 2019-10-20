# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['caroline', 'caroline.databases']

package_data = \
{'': ['*']}

install_requires = \
['addict>=2.2,<3.0',
 'elasticsearch>=6.3,<7.0',
 'jsonschema>=2.6,<3.0',
 'redis>=2.10,<3.0']

extras_require = \
{'ci': ['codacy-coverage>=1.3,<2.0', 'pytest-cov>=2.6,<3.0']}

setup_kwargs = {
    'name': 'caroline',
    'version': '0.5.2',
    'description': 'A key/value-based JSON ODM with a memorable name.',
    'long_description': '# caroline\n\n[![Build Status](https://travis-ci.org/GrafeasGroup/caroline.svg?branch=master)](https://travis-ci.org/GrafeasGroup/caroline)\n[![Codacy Badge](https://api.codacy.com/project/badge/Grade/84632bae1d3f4dd8ad69cf90fd0a8d6b)](https://www.codacy.com/app/joe-kaufeld/caroline?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=GrafeasGroup/caroline&amp;utm_campaign=Badge_Grade)\n[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/84632bae1d3f4dd8ad69cf90fd0a8d6b)](https://www.codacy.com/app/joe-kaufeld/charlotte?utm_source=github.com&utm_medium=referral&utm_content=GrafeasGroup/caroline&utm_campaign=Badge_Coverage)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![Packaged with Poetry](https://img.shields.io/badge/packaged%20with-poetry-blue.svg)](https://poetry.eustace.io)\n\nA key-value JSON ODM with a memorable name.\n\n### What is caroline?\nCaroline is yet another way to store JSON data. It contains backends for Elasticsearch and Redis, and allows you to use both in the same project! Included in the box (and heavily recommended that you use) is jsonschema support.\n\n\n### Why?\nThe existing options that are available didn\'t quite work for what we were looking for, so we wrote our own for internal use and decided to open source it. The goal of the project is easy integration without high overhead.\n\n### How does it work?\n\nThe only thing you need to do to get started is `from caroline import Prototype`. Then you can start building your data classes:\n\n```python\nfrom caroline import Prototype\n\nclass Dog(Prototype):\n    default = {\n        "breed": "",\n        "age": 1,\n        "name": ""\n    }\n    schema = {\n        "type": "object",\n        "properties": {\n            "breed": {\n                "type": "string"\n            },\n            "age": {\n                "type": "number"\n            },\n            "name": {\n                "type": "string"\n            }\n        }\n    }\n    \nsam = Dog(\'sam\')\n\nprint(sam)\n# >>> {"breed": "", "age": 1, "name": ""}\n\nsam.update(\'name\', \'Sam\')\n# OR\nsam[\'name\'] = \'Sam\'\n\nsam.update(\'age\', 5)\nsam.update(\'breed\', \'mutt\')\nsam.save()\n```\nWhen you create a new instance of your class with an ID (like `Dog(\'sam\')`), that\'s the key that the particular record will be saved under. That means that if you create a class with that name, it\'ll load the same record again:\n\n```python\nfrom example_above import Dog\n\nx = Dog(\'sam\')\n\nprint(x)\n# >>> {\'breed\': \'mutt\', \'age\': 5, \'name\': \'Sam\'}\n```\nIf you create an instance of your class with an ID that isn\'t in your chosen database, then it will instantiate it using the `default` dict that you defined in the class. \n\ncaroline will automatically handle its own connections, but if you\'ve got a custom one, feel free to pass it in through your model:\n\n```python\nclass Cat(Prototype):\n    elasticsearch_conn = your_elasticsearch_connection\n    # OR\n    redis_conn = your_redis_connection\n    \n    default = {}\n```\nNOTE: You cannot have more than one connection on your model! Each model can only work with one database; that being said, you _can_ have each model route to a different database if you want to and caroline with handle it for you. If you don\'t want to pass a specific connection with each model, we don\'t blame you; The default connection is Elasticsearch, but you can change that by setting the environment variable `CAROLINE_DEFAULT_DB` to either "elasticsearch" or "redis". You can also import the caroline config directly and manually set the requested database as the default (`caroline.config.default_db = "redis"`).\n\nThere is currently not a way to change the ElasticSearch location, but you can set the Redis location by formatting your Redis address as a URL, (e.g. `redis://localhost:6379/0`) which caroline will pick up if you set it as the environment variable `CAROLINE_REDIS_URL`.\n\nIf time goes on and you need to upgrade your models, we have a plan for that! Just modify your model (add new fields or remove them), then load your keys as normal. Call `.upgrade()` on the object that you\'ve retrieved from the database and caroline will force your existing data into the new model. THIS IS A DESTRUCTIVE CALL.\n\n```python\nfrom caroline import Prototype\n\nclass Dog(Prototype):\n    default = {\n        "age": 1,\n        "name": "",\n        "sire": "",\n        "dam": ""\n    }\n    db = \'redis\'\n\nx = Dog(\'sam\')\nprint(x)\n\n# we get the last time we used the key `sam` for the prototype class `Dog`\n# >>> {\'breed\': \'mutt\', \'age\': 5, \'name\': \'Sam\'}\n\n# THIS CALL RESULTS IN THE DESTRUCTION OF DATA\nx.upgrade()\nprint(x)\n\n# >>> {\'age\': 5, \'name\': \'Sam\', \'sire\': \'\', \'dam\': \'\'}\nx.save()\n```\n\ncaroline also gives you the ability to choose your database root key names; by default, it will be the name of the class model you create. So for example, if you have a class named Dog with the record ID of \'sam\' from above, then the record in the DB will have the key of `::dog::sam`. You can adjust the first part by adding another parameter: `db_key`. Don\'t bother with this unless you have a good reason to change it.\n\nA note on schemas: while we provide support for jsonschema (and that was the driving force behind the creation of this package), you don\'t have to use it -- as the above example illustrates, you don\'t need to create a `schema` key. If no `schema` is passed in, it does not perform the validation step on `.save()` -- otherwise, it validates the data against the schema every time `.save()` is called.\n\nFinally, sometimes you just need a dict; our prototype classes do a great job of pretending to be a dict, but if you ever actually just need the data, call `.to_dict()` and a regular dictionary will be returned.\n',
    'author': 'Grafeas Group Ltd.',
    'author_email': 'devs@grafeas.org',
    'url': 'https://www.grafeas.org',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
