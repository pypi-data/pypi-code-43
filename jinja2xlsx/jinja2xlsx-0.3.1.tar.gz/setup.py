# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['jinja2xlsx']

package_data = \
{'': ['*']}

install_requires = \
['jinja2>=2.10,<3.0', 'openpyxl>=3.0,<4.0', 'requests-html>=0.10.0,<0.11.0']

extras_require = \
{'pil': ['pillow>=6.0,<7.0']}

setup_kwargs = {
    'name': 'jinja2xlsx',
    'version': '0.3.1',
    'description': 'Create xlsx-tables from html-tables',
    'long_description': '# jinja2xlsx\n\nCreate xlsx-tables from html-tables\n\n## Example\n\nGiven html table str\n\nWhen render html to xlsx\n\nThen result xlsx has table values\n\n```python\nfrom jinja2xlsx import render_xlsx\nfrom openpyxl import Workbook\n\nhtml_str = """<!DOCTYPE html>\n<html lang="en">\n    <head>\n        <meta charset="UTF-8">\n        <title>Simple table</title>\n    </head>\n    <body>\n        <table>\n            <tbody>\n                <tr>\n                    <td>1</td>\n                    <td>2</td>\n                </tr>\n                <tr>\n                    <td>3</td>\n                    <td>4</td>\n                </tr>\n            </tbody>\n        </table>\n    </body>\n</html>"""\n\nworkbook: Workbook = render_xlsx(html_str)\nassert tuple(workbook.active.values) == ((1, 2), (3, 4))\n```\n\n## Installation \n\n```\npip install jinja2xlsx\n```\n\nFor images support:\n\n```\npip install jinja2xlsx[pil]\n```\n\n## Development\n\nInstall dependencies:\n\n```\npoetry install\n```\n\nFor images support:\n\n```\npoetry install -E pil\n```\n\nRun tests and linting:\n\n```\npre-commit run -a\n```\n\nInstall pre-commit hooks:\n\n```\npre-commit install\n```\n\n## Extra\n\n### Publish to PyPI\n\n```shell\npoetry publish --build\n```',
    'author': 'potykion',
    'author_email': 'potykion@gmail.com',
    'url': 'https://github.com/potykion/jinja2xlsx',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
