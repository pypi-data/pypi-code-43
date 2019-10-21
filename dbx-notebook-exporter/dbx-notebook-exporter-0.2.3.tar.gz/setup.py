# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['DbxNotebookExporter']

package_data = \
{'': ['*'], 'DbxNotebookExporter': ['Databricks/*', 'Json/*', 'Python/*']}

install_requires = \
['ipython>=7,<8', 'nbconvert>=5,<6']

entry_points = \
{'nbconvert.exporters': ['dbx-json-notebook = '
                         'DbxNotebookExporter.Json.JsonNotebookExporter:JsonNotebookExporter',
                         'dbx-python-notebook = '
                         'DbxNotebookExporter.Python.PythonNotebookExporter:PythonNotebookExporter']}

setup_kwargs = {
    'name': 'dbx-notebook-exporter',
    'version': '0.2.3',
    'description': 'Databrics Notebook Exporter',
    'long_description': 'Databricks Notebook Exporter for nbconvert\n',
    'author': 'Jiri Koutny',
    'author_email': 'jiri.koutny@datasentics.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DataSentics/dbx-notebook-exporter',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5.6,<3.6.0',
}


setup(**setup_kwargs)
