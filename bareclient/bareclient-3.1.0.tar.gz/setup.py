# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['bareclient']

package_data = \
{'': ['*']}

install_requires = \
['baretypes>=3.1,<4.0', 'bareutils>=3.2,<4.0', 'h11>=0.9.0,<0.10.0']

setup_kwargs = {
    'name': 'bareclient',
    'version': '3.1.0',
    'description': 'A lightweight asyncio HTTP client',
    'long_description': "# bareClient\n\nA simple asyncio http client.\n\n## Description\n\nThis package provides the asyncio transport for [h11](https://h11.readthedocs.io/en/latest/index.html).\n\nIt makes little attempt to provide any helpful features.\n\n## Installation\n\nThis is a Python 3.7 package.\n\n```bash\npip install bareclient\n```\n\n## Usage\n\nThe basic usage is to create an `HttpClient`.\n\n```python\nimport asyncio\nfrom bareclient import HttpClient\nimport ssl\n\n\nasync def main(url, headers, ssl):\n    async with HttpClient(url, method='GET', headers=headers, ssl=ssl) as (response, body):\n        print(response)\n        if response.status_code == 200:\n            async for part in body():\n                print(part)\n\n\nurl = 'https://docs.python.org/3/library/cgi.html'\nheaders = [(b'host', b'docs.python.org'), (b'connection', b'close')]\nssl_context = ssl.SSLContext()\n\nloop = asyncio.get_event_loop()\nloop.run_until_complete(main(url, headers, ssl_context))\n```\n\nThere is also an `HttpSession` for keep-alive connections.\n\n```python\nimport asyncio\nfrom bareclient import HttpSession\nimport ssl\n\n\nasync def main(url, headers, paths, ssl):\n    async with HttpSession(url, ssl=ssl) as requester:\n        for path in paths:\n            response, body = await requester.request(path, method='GET', headers=headers)\n            print(response)\n            if response.status_code == 200:\n                async for part in body():\n                    print(part)\n\n\nurl = 'https://docs.python.org'\nheaders = [(b'host', b'docs.python.org'), (b'connection', b'keep-alive')]\npaths = ['/3/library/cgi.html', '/3/library/urllib.parse.html']\nssl_context = ssl.SSLContext()\n\nloop = asyncio.get_event_loop()\nloop.run_until_complete(main(url, headers, paths, ssl_context))\n```\n\nFinally there is a single helper function to get json.\n\n```python\nimport asyncio\nimport ssl\nfrom bareclient import get_json\n\n\nasync def main(url, ssl):\n    obj = await get_json(url, ssl=ssl)\n    print(obj)\n\n\nurl = 'https://jsonplaceholder.typicode.com/todos/1'\nssl_context = ssl.SSLContext()\n\nloop = asyncio.get_event_loop()\nloop.run_until_complete(main(url, ssl_context))\n```",
    'author': 'Rob Blackbourn',
    'author_email': 'rob.blackbourn@gmail.com',
    'url': 'https://github.com/rob-blackbourn/bareclient',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
