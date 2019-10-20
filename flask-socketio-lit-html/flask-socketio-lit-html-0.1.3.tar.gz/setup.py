# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['flask_socketio_lit_html']

package_data = \
{'': ['*'],
 'flask_socketio_lit_html': ['dependencies/*',
                             'webcomponent_templates/*',
                             'webcomponents_static/*']}

install_requires = \
['flask-socketio>=4.2.1,<4.3.0',
 'flask-sqlalchemy>=2.4.0,<2.5.0',
 'flask>=1.1.1,<1.2.0']

setup_kwargs = {
    'name': 'flask-socketio-lit-html',
    'version': '0.1.3',
    'description': 'Simple Webcomponents with flask',
    'long_description': '[![ForTheBadge uses-badges](https://img.shields.io/badge/uses-flask-4ab?style=for-the-badge&labelColor=4cd)](https://palletsprojects.com/p/flask/)\n[![ForTheBadge uses-badges](https://img.shields.io/badge/uses-lit%20html-4ab?style=for-the-badge&labelColor=4cd)](https://lit-html.polymer-project.org/)\n[![ForTheBadge uses-badges](https://img.shields.io/badge/uses-Socket.IO-4ab?style=for-the-badge&labelColor=4cd)](https://socket.io/)\n\n[![Version: Alpha](https://img.shields.io/badge/version-alpha-yellow?style=for-the-badge)](.)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)\n[![Pypi version](https://img.shields.io/pypi/v/flask-socketio-lit-html?style=for-the-badge)](https://pypi.org/project/flask-socketio-lit-html/)\n[![ReadTheDocs](https://readthedocs.org/projects/flask-socketio-lit-html/badge/?version=latest&style=for-the-badge)](https://flask-socketio-lit-html.readthedocs.io/)\n[![Travis (.org)](https://img.shields.io/travis/playerla/flask-socketio-lit-html?style=for-the-badge)](https://travis-ci.org/playerla/flask-socketio-lit-html)\n[![codecov](https://img.shields.io/codecov/c/github/playerla/flask-socketio-lit-html?style=for-the-badge)](https://codecov.io/gh/playerla/flask-socketio-lit-html)\n[![Code Climate maintainability](https://img.shields.io/codeclimate/maintainability/playerla/flask-socketio-lit-html?style=for-the-badge)](https://codeclimate.com/github/playerla/flask-socketio-lit-html)\n\n# Flask-Socket.IO-lit-html\n\nWebcomponents with Flask and SocketIO\n\n[Quick Start on documentation](https://flask-socketio-lit-html.readthedocs.io/introduction.html#introduction)\n\n[Todo App example](https://github.com/playerla/flask-wel-todoapp)\n\n## Proof of concept project to use Webcomponents in Python Flask\n\n* Generate a restful API (inspired from Flask-Restful)\n* Update html on data changes through [socketio](https://socket.io/) (Inspired from Angular properties reflection)\n* Based on the powerful [lit-element library](https://lit-element.polymer-project.org/guide/start)\n\n## Usage philosophy\n\nCreate user webcomponent from sqlalchemy design. GET and POST API on `/user`.\n```python\nclass User(db.Model):\n    username = db.Column(db.String(80), nullable=False)\n\nblueprint = User.configure_blueprint("/user", "user-item", "user.html")\napp.register_blueprint(blueprint)\n```\nDefine the webcomponent view in a jinja template\n```jinja\n{% block render %}\n<strong>${ this.username }</strong>\n{% endblock %}\n```\nDisplay the second user of your database with live update:\n```html\n<script type="module" src="{{url_for(\'user-item.webcomponent\')}}"></script>\n<div> user 2: <user-item index=2 ></user-item></div>\n```\n\nThis code represent the idea behind the module, look at app.py for a working example. Project may be modeled on [wtforms-alchemy](https://github.com/kvesteri/wtforms-alchemy)\n\n## Contribute : Pull requests are welcome !\n\n[![Edit with Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/playerla/flask-socketio-lit-html/tree/Dev)\n\n\n### Updating autodoc\n\n```sh\ncd docs && sphinx-apidoc -o source/ ../flask_socketio_lit_html\n```\n\n### Build and test package\n\n```sh\npoetry build && pip3 install dist/flask_socketio_lit_html* --force-reinstall\n```\n\n### Running browser tests\n```sh\ncd tests ; yarn ; yarn test\n```\nWebcomponent\'s shadow root are disabled when running testcafe (for selecting components)\n\n## Build lit-element with rollup.js\n```sh\ncd flask_socketio_lit_html/dependencies/ && yarn && yarn build && cd ../..\n```\n### Any questions ?\n\n[![Slack Status](https://img.shields.io/badge/slack-join-darkblue?style=for-the-badge)](https://join.slack.com/t/flasksocketio-vhj9931/shared_invite/enQtNzUwMDgzMDg5ODU3LWRhNDg4MmNmMTg2MDYwM2UxYjQ5ZDhkN2FmODY2MGI0NDU3YWNmNTdlOWZkM2YzZmZlMjdmYjNmY2JiZThhOGI)\n\n[![Join the community on Spectrum](https://img.shields.io/badge/Spectrum-join-purple?style=for-the-badge)](https://spectrum.chat/flask-sio-lit-html/)\n\n#### External resources\n\n[Learn webcomponents and lit-element on dev.to](https://dev.to/thepassle/web-components-from-zero-to-hero-4n4m)',
    'author': 'playerla',
    'author_email': 'playerla.94@gmail.com',
    'url': 'https://github.com/playerla/flask-socketio-lit-html',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
