# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['flask_casbin']

package_data = \
{'': ['*']}

install_requires = \
['casbin>=0.8.1,<0.9.0', 'flask>=1.1,<2.0']

setup_kwargs = {
    'name': 'flask-casbin',
    'version': '0.1.0',
    'description': 'Flask Casbin Integration',
    'long_description': 'Flask-Casbin\n============\n\n[![Build Status](https://travis-ci.org/daymien/Flask-Casbin.png?branch=master)](https://travis-ci.org/daymien/Flask-Casbin)\n\n\nFlask-Casbin is an extension that provide Casbin ACL functionality to your Flask project\n\nInstallation\n------------\n\nInstall Flask-Casbin with `pip`:\n\n    pip install Flask-Casbin\n\nInstall Flask-Casbin with `poetry`:\n\n    poetry add Flask-Casbin\n\nExample\n-------\n\nThis is an example Flask application:\n\n```python\nfrom flask import Flask\nfrom flask_casbin import Casbin\n\napp = Flask(__name__)\n\n# config\napp.config["CASBIN_MODEL_CONF"] = "./model.conf"\napp.config["CASBIN_POLICY_CSV"] = "./policy.csv"\n\n# create acl\nacl = Casbin(app)\n\n@app.route(\'/data/<id_:int>\')\ndef get_data(id_):\n    # curent_user ist global authenticated user\n    acl.enforce("user:%s" % current_user.name, "data:%d" % id_, "read") or abort(401)\n\n    # Get data\n    data = db.get_data(id_)\n    return { data_id: data.id, data: data.payload }\n\n```\n\nTodo\n----\n\n* Decorators for ACL check\n* Policy adapters\n* Dynamic Policy Adapter (Flask-SQLAlchemy)\n* More tests\n\nResources\n---------\n\n- [pypi](https://pypi.python.org/pypi/Flask-Casbin)\n- [casbin](https://casbin.org/)\n- [pycasbin](https://github.com/casbin/pycasbin)\n',
    'author': 'Reimund Klain',
    'author_email': 'reimund.klain@condevtec.de',
    'url': 'https://github.com/daymien/Flask-Casbin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
