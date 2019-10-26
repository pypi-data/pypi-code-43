# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['bareasgi', 'bareasgi.basic_router']

package_data = \
{'': ['*']}

install_requires = \
['baretypes>=3.1,<4.0', 'bareutils>=3.2,<4.0']

setup_kwargs = {
    'name': 'bareasgi',
    'version': '3.3.0',
    'description': 'A lightweight ASGI framework',
    'long_description': "# bareASGI\n\nA lightweight ASGI framework (read the [documentation](https://bareasgi.readthedocs.io/en/latest/))\n\n## Status\n\nWork in progress.\n\n## Overview\n\nThis is a _bare_ ASGI web server framework. The goal is to provide\na minimal implementation, with other facilities (serving static files, CORS, sessions, etc.)\nbeing implemented by optional packages.\n\nSome of the features provided by web frameworks are not required for a given app, or conflict with the\nversion or varient required for a given solution. \n\nSee also:\n* [bareASGI-cors](https://github.com/rob-blackbourn/bareasgi-cors) for cross origin resource sharing\n* [bareASGI-static](https://github.com/rob-blackbourn/bareasgi-static) for static file serving\n* [bareASGI-jinja2](https://github.com/rob-blackbourn/bareasgi-jinja2) for Jinja2 template rendering\n* [bareASGI-graphql-next](https://github.com/rob-blackbourn/bareasgi-graphql-next) for GraphQL\n\n## Functionality\n\nThe framework supports:\n* Http,\n* WebSockets,\n* A basic method and path based router,\n* Middleware. \n\n## Examples\n\nThese examples use [uvicorn](https://www.uvicorn.org/) as the ASGI server.\n\n### Simple Client\n\nHere is a simple example which returns some text.\n\n```python\nimport uvicorn\nfrom bareasgi import Application, text_writer\n\nasync def http_request_callback(scope, info, matches, content):\n    return 200, [(b'content-type', b'text/plain')], text_writer('This is not a test')\n\napp = Application()\napp.http_router.add({'GET'}, '/{rest:path}', http_request_callback)\n\nuvicorn.run(app, port=9009)\n```\n\n### Rest Server\n\nHere is a simple rest server.\n\n```python\nimport uvicorn\nimport json\nfrom bareasgi import Application, text_reader, text_writer\n\nasync def get_info(scope, info, matches, content):\n    text = json.dumps(info)\n    return 200, [(b'content-type', b'application/json')], text_writer(text)\n\nasync def set_info(scope, info, matches, content):\n    text = await text_reader(content)\n    data = json.loads(text)\n    info.update(data)\n    return 204, None, None\n\napp = Application(info={'name': 'Michael Caine'})\napp.http_router.add({'GET'}, '/info', get_info)\napp.http_router.add({'POST'}, '/info', set_info)\n\nuvicorn.run(app, port=9009)\n```\n\n### WebSockets\n\nA WebSocket example can be found in the examples folder. Here is the handler.\n\n```python\nasync def test_callback(scope, info, matches, web_socket):\n    await web_socket.accept()\n\n    try:\n        while True:\n            text = await web_socket.receive()\n            if text is None:\n                break\n            await web_socket.send('You said: ' + text)\n    except Exception as error:\n        print(error)\n\n    await web_socket.close()\n```\n\n### Middleware\n\nHere is a simple middleware example.\n\n```python\nimport uvicorn\nfrom bareasgi import Application, text_writer\n\nasync def first_middleware(scope, info, matches, content, handler):\n    info['message'] = 'This is first the middleware. '\n    response = await handler(scope, info, matches, content)\n    return response\n\n\nasync def second_middleware(scope, info, matches, content, handler):\n    info['message'] += 'This is the second middleware.'\n    response = await handler(scope, info, matches, content)\n    return response\n\n\nasync def http_request_callback(scope, info, matches, content):\n    return 200, [(b'content-type', b'text/plain')], text_writer(info['message'])\n\n\napp = Application(middlewares=[first_middleware, second_middleware])\napp.http_router.add({'GET'}, '/test', http_request_callback)\n\nuvicorn.run(app, port=9009)\n```\n",
    'author': 'Rob Blackbourn',
    'author_email': 'rob.blackbourn@gmail.com',
    'url': 'https://github.com/rob-blackbourn/bareasgi',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
