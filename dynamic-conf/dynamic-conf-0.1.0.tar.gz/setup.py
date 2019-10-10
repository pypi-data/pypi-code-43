# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dynamic_conf']

package_data = \
{'': ['*']}

install_requires = \
['six>=1.12,<2.0']

entry_points = \
{'console_scripts': ['dynamic-conf = dynamic_conf:main']}

setup_kwargs = {
    'name': 'dynamic-conf',
    'version': '0.1.0',
    'description': 'Easy to manage Config variables separate from App code. Useful while developing and deploying( CI/CD) django web-apps',
    'long_description': '# dynamic-config\nEasy to manage Config variables separate from App code. Useful while developing and deploying( CI/CD) django web-apps\n\n# Usage\n\n- You need to subclass the `Config` class.\n- Any configuration would be loaded from `python config` file `(default: env.py)` from the same folder where library is \ninherited. This file should not be committed to version history.\n- You also don\'t need to include a sample file. Since the `Config` object would be able to generate `env.py` itself.\n- It also loads Configuration variables from environment variables. The preference is `env variables` > `env.py`\n- The config file should define all the variables needed for a project.\n- It can also define a prefix to limit environment variables searched.\n\n```python\n\n# project/conf.py\n\nfrom dynamic_conf import Config\n\nclass CONFIG(Config):\n    """singleton to be used for configuring from os.environ and env.py"""\n\n    # default settings\n\n    ENV = "prod" # optional field with a default value\n\n    DB_NAME = "db"\n    DB_HOST = "127.0.0.1"\n    DB_USER = "postgres"\n    DB_PASS = None # even None could be given as default value\n\n    SECRET_KEY:str # required field. Note: it will not work in Python 2 because\n```\n\n- to create `project/env.py` just run\n```shell script\n# you could pass environment variables or set already with export\nenv DB_PASS=\'123\' dynamic-conf\n\n# or you could pass as list of key-value pair\ndynamic-conf DB_USER=\'user-1\' DB_PASS=\'123\'\n\n# to filter environment variables with a prefix\nenv VARS_PREFIX="PROD_" dynamic-conf PROD_DB_USER="user-2"\n```\n\n- To use the config simply import and use particular attribute\n```python\n# project/settings.py\nfrom conf import CONFIG\nDATABASES = {\n    "default": {\n        "ENGINE": "django.contrib.gis.db.backends.postgis",\n        "HOST": CONFIG.DB_HOST,\n        "NAME": CONFIG.DB_NAME,\n        "USER": CONFIG.DB_USER,\n        "PASSWORD": CONFIG.DB_PASSWORD,\n        "PORT": "5432",\n    }\n}\n```\n',
    'author': 'Noortheen Raja',
    'author_email': 'jnoortheen@gmail.com',
    'url': 'https://github.com/jnoortheen/dynamic-conf',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*',
}


setup(**setup_kwargs)
