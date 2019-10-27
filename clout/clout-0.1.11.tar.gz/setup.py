# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['clout', 'clout.loaders']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4,<2.0',
 'attrs>=19.2.0',
 'click',
 'dataclasses>=0.6.0,<0.7.0',
 'desert>=0.1.4',
 'glom>=19.2,<20.0',
 'importlib_resources>=1.0,<2.0',
 'inflection>=0.3.1,<0.4.0',
 'lark-parser>=0.7.3,<0.8.0',
 'marshmallow>=3.0,<4.0',
 'typing-extensions>=3.7,<4.0',
 'typing-inspect>=0.4.0,<0.5.0']

setup_kwargs = {
    'name': 'clout',
    'version': '0.1.11',
    'description': 'Command-line Object Utility Tool',
    'long_description': "=======================================================\nClout: Command-Line Object Utility Tool\n=======================================================\n\n.. start-badges\n\n.. list-table::\n    :stub-columns: 1\n\n\n    * - docs\n      - |docs|\n    * - code\n      - |github|\n    * - tests\n      - | |travis|\n        | |codecov|\n    * - package\n      - | |version|\n        | |wheel|\n        | |supported-versions|\n        | |supported-implementations|\n        | |commits-since|\n\n.. |docs| image:: https://img.shields.io/readthedocs/clout\n    :target: https://clout.readthedocs.org\n    :alt: Documentation Status\n\n\n.. |travis| image:: https://img.shields.io/travis/com/python-clout/clout\n    :alt: Travis-CI Build Status\n    :target: https://travis-ci.com/python-clout/clout\n\n.. |version| image:: https://img.shields.io/pypi/v/clout.svg\n    :alt: PyPI Package latest release\n    :target: https://pypi.org/pypi/clout\n\n.. |commits-since| image:: https://img.shields.io/github/commits-since/python-clout/clout/v0.1.11.svg\n    :alt: Commits since latest release\n    :target: https://github.com/python-clout/clout/compare/v0.1.11...master\n\n.. |wheel| image:: https://img.shields.io/pypi/wheel/clout.svg\n    :alt: PyPI Wheel\n    :target: https://pypi.org/pypi/clout\n\n.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/clout.svg\n    :alt: Supported versions\n    :target: https://pypi.org/pypi/clout\n\n.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/clout.svg\n    :alt: Supported implementations\n    :target: https://pypi.org/pypi/clout\n\n.. |codecov| image:: https://img.shields.io/codecov/c/github/python-clout/clout/master.svg\n     :alt: Coverage\n     :target: https://codecov.io/gh/python-clout/clout\n\n.. |github| image:: https://img.shields.io/github/last-commit/python-clout/clout\n     :alt: Last commit\n     :target: https://img.shields.io/github/last-commit/python-clout/clout\n\n.. end-badges\n\n\n\n..\n    start-usage\n\n\nConvert dataclasses into a command-line interface.\n\nQuickstart\n---------------\n\n\nTo install, use\n\n.. code-block:: bash\n\n    pip install clout\n\n\nDefine some dataclasses and convert them into a command-line interface.\n\n\n.. code-block:: python\n\n    import attr\n    import click\n\n    import clout\n\n\n    @attr.dataclass\n    class DB:\n        host: str\n        port: int\n\n\n    @attr.dataclass\n    class Config:\n        db: DB\n        dry_run: bool\n\n\n    cli = clout.Command(type=Config)\n\n    print(cli.build())\n\n\n.. code-block:: bash\n\n    $ myapp config --dry-run db --host example.com --port 9999\n    Config(db=DB(host='example.com', port=9999), dry_run=True)\n\n\n..\n    end-usage\n\nSee the full docs for more information: https://clout.readthedocs.io/\n",
    'author': 'Clout contributors',
    'author_email': 'python-clout@users.noreply.github.com',
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
