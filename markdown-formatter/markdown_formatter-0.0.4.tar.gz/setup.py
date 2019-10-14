# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['markdown_formatter']

package_data = \
{'': ['*']}

install_requires = \
['black>=18.3,<20.0',
 'chardet>=3.0,<4.0',
 'click>=7.0,<8.0',
 'cython>=0.29.13,<0.30.0',
 'mistune>=0.8.4,<0.9.0']

extras_require = \
{':python_version < "3.7"': ['dataclasses>=0.6.0,<0.7.0']}

entry_points = \
{'console_scripts': ['markdown_formatter = markdown_formatter.cli:run_main']}

setup_kwargs = {
    'name': 'markdown-formatter',
    'version': '0.0.4',
    'description': '',
    'long_description': '# A Markdown formatter\n\n![[markdown-formatter](https://pypi.org/project/markdown-formatter/)](https://img.shields.io/pypi/v/markdown-formatter)\n\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/markdown-formatter)\n\n```bash\npip install markdown-formatter\nmarkdown_formatter readme.md\n```\n\nwill apply [black](https://github.com/psf/black) on python code automatically.\n\n\ntable is not implemented yet\n',
    'author': 'Trim21',
    'author_email': 'i@trim21.me',
    'url': 'https://github.com/Trim21/markdown_formatter',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
