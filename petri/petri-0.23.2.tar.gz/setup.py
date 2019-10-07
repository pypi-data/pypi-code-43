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
    'version': '0.23.2',
    'description': 'Free your python code from 12-factor boilerplate.',
    'long_description': '=====\nPETRI\n=====\n\npetri: free your python code from 12-factor boilerplate.\n--------------------------------------------------------\n\n.. list-table::\n   :widths: 50 50\n   :header-rows: 0\n\n   * - Python Version\n     - .. image:: https://img.shields.io/pypi/pyversions/petri\n        :target: https://www.python.org/downloads/\n        :alt: Python Version\n   * - Code Style\n     - .. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n        :target: https://github.com/ambv/black\n        :alt: Code Style\n   * - Release\n     - .. image:: https://img.shields.io/pypi/v/petri\n        :target: https://pypi.org/project/petri/\n        :alt: PyPI\n   * - Downloads\n     - .. image:: https://img.shields.io/pypi/dm/petri\n        :alt: PyPI - Downloads\n   * - Build Status\n     - .. image:: https://github.com/pwoolvett/petri/workflows/publish_wf/badge.svg\n        :target: https://github.com/pwoolvett/petri/actions\n        :alt: Build Status\n   * - Docs\n     - .. image:: https://readthedocs.org/projects/petri/badge/?version=latest\n        :target: https://petri.readthedocs.io/en/latest/?badge=latest\n        :alt: Documentation Status\n   * - Maintainability\n     - .. image:: https://api.codeclimate.com/v1/badges/4a883c99f3705d3390ee/maintainability\n        :target: https://codeclimate.com/github/pwoolvett/petri/maintainability\n        :alt: Maintainability\n   * - License\n     - .. image:: https://img.shields.io/badge/license-Unlicense-blue.svg\n        :target: http://unlicense.org/\n        :alt: License: Unlicense\n   * - Coverage\n     - .. image:: https://api.codeclimate.com/v1/badges/4a883c99f3705d3390ee/test_coverage\n        :target: https://codeclimate.com/github/pwoolvett/petri/test_coverage\n        :alt: Test Coverage\n   * - Deps\n     - .. image:: https://img.shields.io/librariesio/github/pwoolvett/petri\n        :alt: Libraries.io dependency status for GitHub repo\n\n\n------------\n\nSummary\n-------\n\nImporting petri equips your app/pacakage with:\n\n* Dotenv file handling using `python-dotenv <https://pypi.org/project/python-dotenv>`_.\n* Package metadata (for installed packages), using `importlib-metadata <https://pypi.org/project/importlib-metadata>`_.\n* Settings using `pydantic <https://pypi.org/project/pydantic>`_.\n* Logging config using `structlog <https://pypi.org/project/structlog>`_.\n* Environment switching (prod/dev/test) handling via ENV environment variable.\n\n\n.. image:: assets/demo.gif\n :target: https://asciinema.org/a/3vc6LraDAy2v7KQvEoKGRv4sF\n :alt: Sample petri usage\n\nInstall\n-------\n\nInstall using poetry ``poetry add petri`` or pip ``pip install petri``.\n\nOptionally, also install the ``color`` extra for colored logs using `colorama <https://pypi.org/project/colorama>`_.\n\nUsage\n-----\n\n* Define configuration setting(s) and instantiate ``petri.Petri``:\n\n.. code-block:: python\n\n   #  my_package/__init__.py\n\n   from petri import Petri\n   from petri.settings import BaseSettings\n   from petri.loggin import LogFormatter, LogLevel\n\n\n   class Settings(BaseSettings):\n       class Config:\n           env_prefix = "MY_PKG_"  # VERY IMPORTANT!!!\n       # define common settings here\n\n   class Production(Settings):\n       LOG_FORMAT = LogFormatter.JSON\n       LOG_LEVEL = LogLevel.TRACE\n\n\n   class Development(Settings):\n       LOG_FORMAT = LogFormatter.COLOR  # requires colorama\n       LOG_LEVEL = LogLevel.WARNING\n\n\n   pkg = Petri(__file__)\n\n   # demo logs\n   pkg.log.info("log away info level",mode=pkg.settings, version=pkg.meta.version)\n   pkg.log.warning("this will show", kewl=True)\n\n.. note::\n\n   You **must** define ``Config.env_prefix`` inside your setting class\n   (see above). This allows `petri` to select settings class using envvars.\n\n   As an example, a package named ``my-pkg`` should have its setting(s) classes:\n\n   1. Inherit from ``petri.BaseSettings``\n   2. Contain a ``Config`` subclass (just like for ``pydantic``\'s), with its\n      ``env_prefix`` set to  ``"MY_PKG_"``.\n\n\n   The code used should be compatible with:\n\n     ``Config.env_prefix=[package_name].upper().replace(\'-\' ,\'_\')+\'_\'``.\n\n     (See `petri.Petri.pkg_2_envvar`.)\n\n* [OPTIONAL] Define an environment variable named `env_file`, to feed\n   additional envs. Its value must be the path to a valid, existing file.\n\n* Select which of your settings classes to use, by doing one of the folowing:\n\n   + Point the selector envvar (eg: for `a-pkg`, this would be\n     `A_PKG_CONFIG=a_pkg.settings:Production`, see `petri.Petri.pkg_2_envvar`),\n     or\n\n   + Use the `default_config` kwarg when instantiating `petri.Petri`\n     (See below)\n\n   Of course, you can use both. Petri will attempt to load said env, and if not\n   found, default to the defined kwarg.\n\nAdditional Info\n---------------\n\n- Load `env_file`\'s contents, if defined.\n- Provide your package\'s metadata (version, author, etc), available in\n  `pkg.meta` (lazy-loaded to avoid reading metadata files unnecessarily).\n- Activate and instantiate a settings class, according to environment var and\n  default, available in `pkg.settings` (https://pydantic-docs.helpmanual.io/#id5)\n- Configure and expose a logger, available in `pkg.log`, which uses\n  configuration defined in your settings.\n\n-----\n\nFor more info, check the `docs <https://petri.rtfd.org>`_.\n',
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
