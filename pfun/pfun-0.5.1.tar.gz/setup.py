# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pfun']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=3.7,<4.0']

setup_kwargs = {
    'name': 'pfun',
    'version': '0.5.1',
    'description': '',
    'long_description': '# <img src="https://raw.githubusercontent.com/suned/pfun/master/logo/pfun_logo.svg?sanitize=true" style=" width:50px ; height:50px "/>\n\n\n- [Documentation](https://pfun.readthedocs.io/en/latest/)\n- [Examples](https://github.com/suned/pfun/tree/master/examples)\n- [Known issues](https://github.com/suned/pfun/issues?q=is%3Aopen+is%3Aissue+label%3Abug)\n\n## Install\n\n`pip install pfun`\n\n## Support\n\nOn [ko-fi](https://ko-fi.com/python_pfun)\n\n## Development\n\nRequires [poetry](https://poetry.eustace.io/)\n\n- Install dependencies with `poetry install`\n- Build documentation with `poetry run sphinx-build -b html docs/source docs/build`\n- Run tests with `poetry run pytest`',
    'author': 'Sune Debel',
    'author_email': 'sad@archii.ai',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
