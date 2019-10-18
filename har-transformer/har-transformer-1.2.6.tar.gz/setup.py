# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['transformer', 'transformer.plugins']

package_data = \
{'': ['*']}

install_requires = \
['chevron>=0.13,<0.14',
 'dataclasses>=0.6.0,<0.7.0',
 'docopt>=0.6.2,<0.7.0',
 'ecological>=1.6,<2.0',
 'pendulum>=2.0,<3.0',
 'requests>=2.21,<3.0']

extras_require = \
{'docs': ['sphinx>=1.8,<2.0',
          'sphinx-autodoc-typehints>=1.6,<2.0',
          'sphinx-issues>=1.2,<2.0']}

entry_points = \
{'console_scripts': ['transformer = transformer.cli:script_entrypoint']}

setup_kwargs = {
    'name': 'har-transformer',
    'version': '1.2.6',
    'description': 'A tool to convert HAR files into a locustfile.',
    'long_description': '\n.. image:: docs/_static/transformer.png\n   :alt: Transformer logo\n   :align: center\n\n|\n\n.. image:: https://travis-ci.org/zalando-incubator/Transformer.svg?branch=master\n   :alt: travis-ci status badge\n   :target: https://travis-ci.org/zalando-incubator/Transformer\n\n.. image:: https://badgen.net/pypi/v/har-transformer\n   :alt: pypi version badge\n   :target: https://pypi.org/project/har-transformer\n\n.. image:: https://api.codacy.com/project/badge/Grade/10b3feb4e4814429bf288b87443a6c72\n   :alt: code quality badge\n   :target: https://www.codacy.com/app/thilp/Transformer\n\n.. image:: https://api.codacy.com/project/badge/Coverage/10b3feb4e4814429bf288b87443a6c72\n   :alt: test coverage badge\n   :target: https://www.codacy.com/app/thilp/Transformer\n\n.. image:: https://badgen.net/badge/code%20style/black/000\n   :alt: Code style: Black\n   :target: https://github.com/ambv/black\n\n\nTransformer\n***********\n\nA **command-line tool** and **Python library** to convert web browser sessions\n(`HAR`_ files) into Locust_ load test scenarios ("locustfiles").\n\n.. _HAR: https://en.wikipedia.org/wiki/.har\n.. _Locust: https://locust.io/\n\nUse it to **replay HAR files** (storing recordings of interactions with your\nwebsite) **in load tests** with Locust_.\n\n.. contents::\n   :local:\n\nInstallation\n============\n\nInstall from PyPI::\n\n   pip install har-transformer\n\nUsage\n=====\n\nExample HAR files are included in the ``examples/`` directory, try them\nout.\n\nCommand-line\n------------\n\n.. code:: bash\n\n   transformer my_har_files_directory/ >locustfile.py\n\nLibrary\n-------\n\n.. code:: python\n\n   import transformer\n\n   with open("locustfile.py", "w") as f:\n       transformer.dump(f, ["my_har_files_directory/"])\n\nDocumentation\n=============\n\nTake a look at our documentation_ for more details, including how to **generate\nHAR files**, **customize your scenarios**, use or write **plugins**, etc.\n\n.. _documentation: https://transformer.readthedocs.io/\n\nAuthors\n=======\n\n- **Serhii Cherniavskyi** — `@scherniavsky <https://github.com/scherniavsky>`_\n\n- **Thibaut Le Page** — `@thilp <https://github.com/thilp>`_\n\n- **Brian Maher** — `@bmaher <https://github.com/bmaher>`_\n\n- **Oliwia Zaremba** — `@tortila <https://github.com/tortila>`_\n\nSee also the list of contributors_ to this project.\n\n.. _contributors: https://transformer.readthedocs.io/en/latest/Contributors.html\n\nLicense\n=======\n\nThis project is licensed under the MIT license — see the LICENSE.md_ file for\ndetails.\n\n.. _LICENSE.md: https://github.com/zalando-incubator/Transformer/blob/master\n   /LICENSE.md\n',
    'author': 'Serhii Cherniavskyi',
    'author_email': 'serhii.cherniavskyi@zalando.de',
    'url': 'https://transformer.readthedocs.io/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
