# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['log_enricher']

package_data = \
{'': ['*']}

install_requires = \
['python-json-logger>=0.1.11,<0.2.0',
 'sorcery>=0.2.0,<0.3.0',
 'strenum>=0.4.0,<0.5.0']

setup_kwargs = {
    'name': 'log-enricher',
    'version': '0.1.3',
    'description': 'Library to enrich structured logs',
    'long_description': 'log-enricher\n============\n[![CircleCI](https://circleci.com/gh/arni-inaba/log-enricher.svg?style=svg)](https://circleci.com/gh/arni-inaba/log-enricher)\n[![PyPI Downloads](https://img.shields.io/pypi/dm/log-enricher.svg)](https://pypi.org/project/log-enricher/)\n[![PyPI Version](https://img.shields.io/pypi/v/log-enricher.svg)](https://pypi.org/project/log-enricher/)\n[![License](https://img.shields.io/badge/license-mit-blue.svg)](https://pypi.org/project/log-enricher/)\n\nThis is a log enricher, useful for adding custom fields to log records.\n\nThis was developed at [GRID](https://github.com/GRID-is) for use with our\npython backend services and intended to emit structured logs.\n\ninstallation\n------------\n```\npip install log-enricher\n```\n\nconfiguration\n-------------\n\nThe log-enricher takes in a list of functions that return a dictionary:\n```python\nimport os\n\nfrom log_enricher import initialize_logging, Level\nfrom app import current_user_context\n\ndef main():\n    extra_log_properties = {\n        "app_version": os.environ.get("APP_VERSION", "N/A"),\n        "release_stage": os.environ.get("RELEASE_STAGE", "unknown"),\n    }\n    initialize_logging(\n        loggers=["uvicorn", "sqlalchemy"],\n        structured_logs=os.environ.get("STRUCTURED_LOGS", True),\n        log_level=Level.INFO,\n        enrichers=[current_user_context, lambda: extra_log_properties],\n    )\n```\nLogs will be output in a structured JSON format if `structured_logs` is `True`,\nor in a plain, console-friendly format if it is `False`.\n\nenrichers\n---------\nTo build a log enricher, make a subclass of Enricher, or Callable, and implement `__call__()`. Any method returning \na dict can be used to enrich log records. See [log_enricher/enrichers.py](log_enricher/enrichers.py). The key-value\npairs in the dict are added as attribute-value pairs to the log record. Of course, any method calls in the \nenrichers need to  work in any subsequent context the logging system is called.\n',
    'author': 'Arni Inaba Kjartansson',
    'author_email': 'arni@grid.is',
    'url': 'https://github.com/arni-inaba/log-enricher',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
