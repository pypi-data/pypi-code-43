# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['petri']

package_data = \
{'': ['*']}

install_requires = \
['importlib_metadata>=0.23,<0.24',
 'pydantic>=0.32.2,<0.33.0',
 'python-dotenv>=0.10.3,<0.11.0',
 'structlog>=19.1.0,<20.0.0']

extras_require = \
{'color': ['colorama>=0.4.1,<0.5.0']}

setup_kwargs = {
    'name': 'petri',
    'version': '0.24.0',
    'description': 'Free your python code from 12-factor boilerplate.',
    'long_description': '=====\nPETRI\n=====\n\npetri: free your python code from 12-factor boilerplate.\n--------------------------------------------------------\n\n.. list-table::\n   :widths: 50 50\n   :header-rows: 0\n\n   * - Python Version\n     - .. image:: https://img.shields.io/pypi/pyversions/petri\n        :target: https://www.python.org/downloads/\n        :alt: Python Version\n   * - Code Style\n     - .. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n        :target: https://github.com/ambv/black\n        :alt: Code Style\n   * - Release\n     - .. image:: https://img.shields.io/pypi/v/petri\n        :target: https://pypi.org/project/petri/\n        :alt: PyPI\n   * - Downloads\n     - .. image:: https://img.shields.io/pypi/dm/petri\n        :alt: PyPI - Downloads\n   * - Build Status\n     - .. image:: https://github.com/pwoolvett/petri/workflows/publish_wf/badge.svg\n        :target: https://github.com/pwoolvett/petri/actions\n        :alt: Build Status\n   * - Docs\n     - .. image:: https://readthedocs.org/projects/petri/badge/?version=latest\n        :target: https://petri.readthedocs.io/en/latest/?badge=latest\n        :alt: Documentation Status\n   * - Maintainability\n     - .. image:: https://api.codeclimate.com/v1/badges/4a883c99f3705d3390ee/maintainability\n        :target: https://codeclimate.com/github/pwoolvett/petri/maintainability\n        :alt: Maintainability\n   * - License\n     - .. image:: https://img.shields.io/badge/license-Unlicense-blue.svg\n        :target: http://unlicense.org/\n        :alt: License: Unlicense\n   * - Coverage\n     - .. image:: https://api.codeclimate.com/v1/badges/4a883c99f3705d3390ee/test_coverage\n        :target: https://codeclimate.com/github/pwoolvett/petri/test_coverage\n        :alt: Test Coverage\n   * - Deps\n     - .. image:: https://img.shields.io/librariesio/github/pwoolvett/petri\n        :alt: Libraries.io dependency status for GitHub repo\n\n\n------------\n\nSummary\n-------\n\n\nImporting petri equips your app/pacakage with:\n\n* Dotenv file handling using `python-dotenv <https://pypi.org/project/python-dotenv>`_.\n* Package metadata (for installed packages), using `importlib-metadata <https://pypi.org/project/importlib-metadata>`_.\n* Settings using `pydantic <https://pypi.org/project/pydantic>`_.\n* Logging config using `structlog <https://pypi.org/project/structlog>`_.\n* Environment switching (prod/dev/test) handling via ENV environment variable.\n\n\n.. image:: assets/demo.gif\n :target: https://asciinema.org/a/3vc6LraDAy2v7KQvEoKGRv4sF\n :alt: Sample petri usage\n\n\nMotivation\n----------\n\n* In order to have same code for dev/production, it all starts with an innocent\n  `settings.py`.\n* In order to switch between them, it\'s a\n  `good <https://docs.djangoproject.com/en/2.2/topics/settings/#designating-the-settings>`_\n  `idea <https://flask.palletsprojects.com/en/1.1.x/config/#development-production>`_\n  `to <https://12factor.net/config>`_ use env vars...\n* But sometimes, you want to overrride a single variable.\n* But sometimes, you want to overrride several variables.\n* Plus, colored logs while developing are pretty.\n* Plus, structured logs in production look smart.\n\n\nFeatures\n--------\n\n\n- [X] Sane defaults for logging:\n\n  - [X] json logs for production.\n  - [X] user-friendly (spaced) + colored for development.\n  - [X] Enforce root logger\'s formatting.\n- [X] Easy settings:\n\n  - [X] Toggle between configurations using a signle env var.\n  - [X] Define default configuration in case the env var is not present.\n  - [X] Granular settings override using environment variables.\n  - [X] Batch settings override by loading a `.env`.\n- Read package metadata (author, version, etc):\n\n  - [X] Lazy-loaded to avoid reading files during imports.\n  - [X] For installed packages only.\n\n\nInstall\n-------\n\nInstall using\npoetry ``poetry add petri`` or\npip ``pip install petri`` or\n(for dev) ``pip install git+https://github.com/pwoolvett/petri``.\n\nOptionally, also install the ``color`` extra for colored logs using `colorama <https://pypi.org/project/colorama>`_.\n\nUsage\n-----\n\nJust fefine configuration setting(s) and instantiate ``petri.Petri``:\n\n.. code-block:: python\n\n   #  my_package/__init__.py\n\n   from petri import Petri\n   from petri.settings import BaseSettings\n   from petri.loggin import LogFormatter, LogLevel\n\n\n   class Settings(BaseSettings):\n       SQL_CONNECTION_STRING = \'sqlite:///database.db\'  # example setting\n\n   class Production(Settings):\n       LOG_FORMAT = LogFormatter.JSON\n       LOG_LEVEL = LogLevel.TRACE\n\n\n   class Development(Settings):\n       LOG_FORMAT = LogFormatter.COLOR  # requires colorama\n       LOG_LEVEL = LogLevel.WARNING\n\n\n   pkg = Petri(__file__)\n\n   # demo logs\n   pkg.log.info("log away info level",mode=pkg.settings, version=pkg.meta.version)\n   pkg.log.warning("this will show", kewl=True)\n\nThat\'s it!. Watch the animation above for results running\n`python -c "import my_package"`\n\nOptionally, define an environment variable named `env_file`, to override\nthe settings:\n\n   - Its value must be the path to a valid, existing file.\n   - Its contents must have name=value pairs.\n   - The names must be of the form `[MY_PACKAGE]_[SETTING_NAME]`\n     (Watch the animation above).\n\nTo select which of your settings classes to use, you can:\n\n   + Point the selector envvar (eg: for `my-pkg`, this would be\n     `MY_PKG_CONFIG=my_pkg.settings:Production`),\n     or\n\n   + Use the `default_config` kwarg when instantiating `petri.Petri`\n     (eg: use `pkg = Petri(__file__, default_config="my_pkg.settings:Production")`\n     in the example above).\n\n   Of course, you can use both. Petri will attempt to load the selecto envvar,\n   and if not found, default to the defined kwarg.\n\n-----\n\nFor more info, check the `docs <https://petri.rtfd.org>`_.\n',
    'author': 'Pablo Woolvett',
    'author_email': 'pablowoolvett@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/petri/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
