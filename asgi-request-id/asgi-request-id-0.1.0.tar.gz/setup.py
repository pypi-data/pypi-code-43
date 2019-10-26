# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['asgi_request_id']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'asgi-request-id',
    'version': '0.1.0',
    'description': 'ASGI request id middleware',
    'long_description': 'asgi-request-id\n===============\n\nThis was developed at [GRID](https://github.com/GRID-is) for use with our\npython backend services and intended to make it easier to log/generate \nrequest IDs.\n\ninstallation\n------------\n```\npip install asgi-request-id\n```\n\nusage\n-----\n```python\nimport logging\nimport uvicorn\n\nfrom starlette.applications import Starlette\nfrom starlette.responses import PlainTextResponse\n\nfrom asgi_request_id import RequestIDMiddleware, get_request_id\n\nlogger = logging.getLogger(__name__)\napp = Starlette()\n\n\n@app.route("/")\ndef homepage(request):\n    logger.info(f"Request ID: {get_request_id()}")\n    return PlainTextResponse("hello world")\n\n\napp.add_middleware(\n    RequestIDMiddleware,\n    incoming_request_id_header="x-amzn-trace-id",\n    prefix="myapp-",\n)\n\nif __name__ == "__main__":\n    uvicorn.run(app)\n```\nThe package will do the following:\n\nSearch for an incoming request identifier and use it as the request id if found.\nIf it is not found, an unique request id with an optional prefix is generated.\n\nThe request id is stored in a context variable and made available via \n`get_request_id`\n\nFinally, it is set as the `request_id` response header.',
    'author': 'Arni Inaba Kjartansson',
    'author_email': 'arni@inaba.is',
    'url': 'https://github.com/arni-inaba/asgi-request-id',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
