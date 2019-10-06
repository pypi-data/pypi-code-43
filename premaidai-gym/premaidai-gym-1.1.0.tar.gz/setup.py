# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['premaidai_gym']

package_data = \
{'': ['*'], 'premaidai_gym': ['assets/*', 'assets/meshes/*']}

install_requires = \
['gym>=0.10.5,<0.11.0', 'numpy>=1.17,<2.0', 'roboschool>=1.0,<2.0']

setup_kwargs = {
    'name': 'premaidai-gym',
    'version': '1.1.0',
    'description': 'Roboshcool env for Premaid AI',
    'long_description': "premaidai-gym: プリメイドAIのRoboschool gym env\n\n---------------\nインストール\n---------------\n\ncode-block:: bash\n\n    $ pip install premaidai_gym\n\n---------------\n使い方\n---------------\n\ncode-block:: python\n\n    import gym\n    import premaidai_gym\n\n    env = gym.make('RoboschoolPremaidAIWalker-v0')\n",
    'author': 'Shundo Kishi',
    'author_email': 'syundo0730@gmail.com',
    'url': 'https://github.com/syundo0730/premaidai-gym',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
