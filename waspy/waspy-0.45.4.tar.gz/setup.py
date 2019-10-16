# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['waspy', 'waspy.listeners', 'waspy.transports']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML', 'aenum==1.4.5', 'aioamqp', 'httptools']

setup_kwargs = {
    'name': 'waspy',
    'version': '0.45.4',
    'description': 'Async Microservices Framework',
    'long_description': '# WASPy\n\nWaspy is the python framework for the [WASP project](https://github.com/wasp/wasp). \n    In other words its an asynchronous "transport-agnostic" web framework.\n\n## Language agnostic concepts\nWhile this framework is for python, the patterns used in wasp are language\nagnostic. You should be able to call other services in different languages\nassuming they all follow the same patterns. This framework has a pluggable\narchitecture for the transport layer, which allows you to switch from\nhttp to using a message bus, or vice-versa. You could even listen on both\nat the same time without having to modify your code at all.\n\n## Example\nLook at `examples/` folder for some quick examples, or there is an entire example repo at https://github.com/wasp/waspy-example\n\n## Alpha\nThis project is currently in alpha state. \nThere are a lot of features missing.\n\nFeatures for beta:\n- [x] HTTP Transport\n- [x] Routing\n- [x] RabbitMQ transporty\n- [x] Support middlewares\n- [x] Client library (for calling other services)\n- [x] HTTP client transport (with envvar service discovery)\n- [x] RabbitMQ client transport\n- [ ] Test everything\n\nnote: all alpha features are complete, but I am still in the process of adding more robusts tests. Until that is done, waspy will remain in alpha and api\'s might change.\n \nWish List:\n- [ ] Transport classes for nats (nats.io)\n- [ ] Transport classes for kafka\n- [ ] Transport classes for gRPC \n- [ ] pattern for synchronous "worker-tier"\n- [x] configuration package\n- [ ] auto-reloading when in debug mode\n- [x] sentry integration\n- [ ] jwt handling\n\nFeatures for GA (1.0):\n- [ ] High level "Falcon-like" api for writing RESTFUL endpoints even easier!\n- [ ] High level can be overridden by lower level for control/performance reasons\n- [ ] Stable/proven API\n\n## License\nApache-2.0\n\n## Installing\nTo install, just run `pip install waspy`\n\n## Developing\n`python setup.py develop`\n',
    'author': 'Nick Humrich',
    'author_email': 'nhumrich@canopytax.com',
    'url': 'https://github.com/wasp/waspy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
