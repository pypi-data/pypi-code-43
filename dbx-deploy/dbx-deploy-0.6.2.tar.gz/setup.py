# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['DbxDeploy']

package_data = \
{'': ['*'],
 'DbxDeploy': ['Cluster/*',
               'Dbc/*',
               'Git/*',
               'Job/*',
               'Logger/*',
               'Notebook/*',
               'Notebook/Converter/*',
               'Requirements/*',
               'Setup/*',
               'Setup/Version/*',
               'String/*',
               'Whl/*',
               'Workspace/*',
               '_config/*']}

install_requires = \
['PyYAML>=5,<6',
 'colorlog>=4,<5',
 'databricks-api>=0.3,<0.4',
 'dbx-notebook-exporter>=0.2,<0.3',
 'injecta>=0.4,<0.5',
 'nbconvert>=5,<6',
 'pygit2<1.0.0',
 'python-box>=3,<4']

entry_points = \
{'console_scripts': ['dbx-delete-all-jobs = '
                     'DbxDeploy.JobsDeleterCommand:JobsDeleterCommand.run',
                     'dbx-deploy = '
                     'DbxDeploy.DeployerCommand:DeployerCommand.run',
                     'dbx-deploy-submit-job = '
                     'DbxDeploy.DeployerJobSubmitterCommand:DeployerJobSubmitterCommand.run',
                     'dbx-deploy-with-cleanup = '
                     'DbxDeploy.DeployWithCleanupCommand:DeployWithCleanupCommand.run']}

setup_kwargs = {
    'name': 'dbx-deploy',
    'version': '0.6.2',
    'description': 'Databrics Deployment Tool',
    'long_description': 'Databricks project deployment package\n',
    'author': 'Jiri Koutny',
    'author_email': 'jiri.koutny@datasentics.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DataSentics/dbx-deploy',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5.6,<3.6.0',
}


setup(**setup_kwargs)
