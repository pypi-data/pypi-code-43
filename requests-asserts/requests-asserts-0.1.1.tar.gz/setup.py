# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['requests_asserts']
install_requires = \
['requests>=2.22,<3.0', 'responses>=0.10.6,<0.11.0']

setup_kwargs = {
    'name': 'requests-asserts',
    'version': '0.1.1',
    'description': 'The library to help test your HTTP requests using unittests',
    'long_description': 'Used to mock response and validate that the requests happened in the right order with right data\n\nUsage example:\n```py\nimport requests\nfrom unittests import TestCase \n\ndef get_likes_on_post(username, password, post_id):\n    access_token = requests.post(\'http://my.site/login\',\n                                 json={\'username\': username, \'password\': password}).json()[\'access_token\']\n\n    likes = requests.get(f\'http://my.site/posts/{post_id}\',\n                         headers={\'Accept\': \'application/json\',\n                                  \'Authorization\': f\'Bearer {access_token}\'}).json()[\'likes\']\n\n    return likes\n\nclass TestGetLikesOnPost(TestCase):\n    @RequestMock.assert_requests([\n        RequestMock(\n            request_url=\'http://my.site/login\',\n            request_json={\'username\': \'the name\', \'password\': \'the password\'},\n            request_method=RequestMock.Method.POST,\n            response_json={"access_token": \'the-token\'}\n        ),\n        RequestMock(\n            request_url=\'http://my.site/posts/3\',\n            request_headers_contains={\'Authorization\': \'Bearer the-token\'},\n            response_json={\'name\': \'The cool story\', \'likes\': 42}\n        )\n    ])\n    def test_get_likes_on_post(self):\n        self.assertEqual(42, get_likes_on_post(\'the name\', \'the password\', 3))\n\n```\n',
    'author': 'Adrian Dankiv',
    'author_email': 'adr-007@ukr.net',
    'url': 'https://github.com/ADR-007/requests-asserts',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
