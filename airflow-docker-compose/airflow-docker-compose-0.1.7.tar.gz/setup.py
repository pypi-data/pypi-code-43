# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['airflow_docker_compose']

package_data = \
{'': ['*']}

install_requires = \
['click', 'docker', 'docker-compose', 'python-dotenv', 'toml']

entry_points = \
{'console_scripts': ['airflow-docker-compose = '
                     'airflow_docker_compose.__main__:run']}

setup_kwargs = {
    'name': 'airflow-docker-compose',
    'version': '0.1.7',
    'description': '',
    'long_description': "# airflow-docker-compose\n[![CircleCI](https://circleci.com/gh/airflowdocker/airflow-docker-compose.svg?style=svg)](https://circleci.com/gh/airflowdocker/airflow-docker-compose) [![codecov](https://codecov.io/gh/airflowdocker/airflow-docker-compose/branch/master/graph/badge.svg)](https://codecov.io/gh/airflowdocker/airflow-docker-compose)\n\n## Description\nA reasonably light wrapper around `docker-compose` to make it simple to start a local\nairflow instance in docker.\n\n## Usage\n\n```bash\nairflow-docker-compose --help\nairflow-docker-compose up\n```\n\n\n## Configuration\n\nIn order to use this tool, you should have a local `dags` folder containing your dags.\nYou should also have a `pyproject.toml` file which minimally looks like\n\n```ini\n[tool.airflow-docker-compose]\ndocker-network = 'network-name'\n```\n\nIn order to set airflow configuration, you can use the `airflow-environment-variables` key.\nThis allows you to set any `airflow.cfg` variables like so:\n\n```ini\n[tool.airflow-docker-compose]\nairflow-environment-variables = {\n    AIRWFLOW_WORKER_COUNT = 4\n    AIRFLOW__AIRFLOWDOCKER__FORCE_PULL = 'false'\n}\n",
    'author': 'Dan Cardin',
    'author_email': 'ddcardin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/airflowdocker/airflow-docker-compose',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5.0',
}


setup(**setup_kwargs)
