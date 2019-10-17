# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['jetblack_metrics', 'jetblack_metrics.metrics']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'jetblack-metrics',
    'version': '1.0.0',
    'description': 'Generic metrics and context bases monitoring',
    'long_description': '# jetblack-metrics\n\nGeneric metric classes and context based monitoring.\n\n## Installation\n\nInstall from the pie store.\n\n```bash\npip install jetblack-metrics\n```\n\n## Usage\n\nFirst you need to implement a metric which interacts with an actual\ninstrumentation implementation. The following provides an HTTP request\nmetric using Prometheus to gather the metrics and the `TimedMetric` to\nprovide a latency metric.\n\n```python\nfrom jetblack_metrics import monitor, TimedMetric\nfrom prometheus_client import Counter, Gauge, Histogram\n\nclass HttpRequestMetric(TimedMetric):\n    """\n    A metric which holds HTTP information.\n    """\n\n    def __init__(self, name: str, method: str, path: str) -> None:\n        super().__init__()\n        self.name = name\n        self.scope = method\n        self.info = path\n        self.status = 500\n\n    REQUEST_COUNT = Counter(\n        "http_request_count",\n        "Number of requests received",\n        ["name", "method", "path", "status"]\n    )\n    REQUEST_LATENCY = Histogram(\n        "http_request_latency",\n        "Elapsed time per request",\n        ["name", "method", "path"]\n    )\n    REQUEST_IN_PROGRESS = Gauge(\n        "http_requests_in_progress",\n        "Requests in progress",\n        ["name", "method", "path"]\n    )\n\n    def on_enter(self):\n        super().on_enter()\n        self.REQUEST_IN_PROGRESS.labels(\n            self.name,\n            self.scope[\'method\'],\n            self.scope[\'path\']\n        ).inc()\n\n    def on_exit(self) -> None:\n        super().on_exit()\n        self.REQUEST_COUNT.labels(\n            self.name,\n            self.scope[\'method\'],\n            self.scope[\'path\'],\n            self.status\n        ).inc()\n        self.REQUEST_LATENCY.labels(\n            self.name,\n            self.scope[\'method\'],\n            self.scope[\'path\']\n        ).observe(self.elapsed)\n        self.REQUEST_IN_PROGRESS.labels(\n            self.name,\n            self.scope[\'method\'],\n            self.scope[\'path\']\n        ).dec()\n```\n\nOnce we have the metric we can use the `monitor` function to manage the process\nof gathering the statistics.\n\n```python\ndef some_http_middleware(request, next_handler):\n    """Some kind of HTTP middleware function"""\n    with monitor(HttpRequestMetric(\'MyApp\', request.method, request.path)) as metric:\n        # Call the request handler\n        response = next_handler(request)\n        metric.status = response.status\n```\n',
    'author': 'Rob Blackbourn',
    'author_email': 'rob.blackbourn@gmail.com',
    'url': 'https://github.com/rob-blackbourn/jetblack-metrics',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
