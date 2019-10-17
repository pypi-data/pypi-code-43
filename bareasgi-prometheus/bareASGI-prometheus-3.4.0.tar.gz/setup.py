# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['bareasgi_prometheus', 'bareasgi_prometheus.metrics']

package_data = \
{'': ['*']}

install_requires = \
['bareASGI>=3.0,<4.0',
 'baretypes>=3.0.5,<4.0.0',
 'bareutils>=3.1,<4.0',
 'jetblack-metrics>=1.0,<2.0',
 'prometheus_client>=0.7.1,<0.8.0']

setup_kwargs = {
    'name': 'bareasgi-prometheus',
    'version': '3.4.0',
    'description': 'Prometheus metrics for bareASGI',
    'long_description': "# bareASGI-prometheus\n\nPrometheus metrics for bareASGI\n\n## Installation\n\nInstall from the pie store\n\n```bash\n$ pip install bareASGI-prometheus\n```\n\n## Usage\n\nThe middleware can either be configured manually or with a helper.\n\n### Manual Configuration\n\n```python\nfrom bareasgi import Application\nfrom bareasgi_prometheus import PrometheusMiddleware, prometheus_view\n\n...\n\nprometheus_middleware = PrometheusMiddleware()\napp = Application(middlewares=[prometheus_middleware])\napp.http_router.add({'GET'}, '/metrics', prometheus_view)\n```\n\n\n### Helper Configuration\n\n```python\nfrom bareasgi import Application\nfrom bareasgi_prometheus import add_prometheus_middleware\n\n...\n\napp = Application()\nadd_prometheus_middleware(app)\n```\n",
    'author': 'Rob Blackbourn',
    'author_email': 'rob.blackbourn@gmail.com',
    'url': 'https://github.com/rob-blackbourn/bareASGI-prometheus',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
