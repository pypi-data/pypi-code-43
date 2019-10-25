# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['statsapiclient', 'statsapiclient.games']

package_data = \
{'': ['*']}

install_requires = \
['jupyter>=1.0,<2.0', 'requests>=2.21,<3.0']

setup_kwargs = {
    'name': 'statsapiclient',
    'version': '0.1.2',
    'description': 'A wrapper around the NHL’s JSON API.',
    'long_description': "# statsapiclient: A client for the NHL stats API\n\n[![CircleCI](https://circleci.com/gh/bplabombarda/statsapiclient.svg?style=svg)](https://circleci.com/gh/bplabombarda/statsapiclient)\n\n## Purpose\n\nTo provide a Python client to access the NHL's JSON API including game, play, and player data.\n\n\n## Installation\n\n    pip install -i https://test.pypi.org/simple/ statsapiclient\n\n\n## Modules\n\n### Schedule\n\n`get_games`\n\nReturns a list of games contained within the instantiated date or date range.\n\n\n### Games\n\n#### game\n\n`get_box_score`\n\n`get_line_score`\n\n`get_play_by_play`\n\n\n### Teams\n\n`get_active`\n\nReturns a list of all active teams.\n\n`get_active_by_conference`\n\nReturns a list of all active teams in a given conference.\n\n`get_active_by_division`\n\nReturns a list of all active teams in a given division.\n\n\n### Examples\n\nGames from date:\n      \n    from statsapiclient.schedule import Schedule\n\n\n    s = Schedule('2019-01-01')\n    games = s.get_games()\n\n    print(games[0]['gamePk'])    # 2018020612\n\nGame data:\n\n    from statsapiclient.games.game import Game\n\n    g = Game('2018020612')\n\n    box_score = g.get_box_score()\n    line_score = g.get_line_score()\n    play_by_play = g.get_play_by_play()\n\nFor more: [Jupyter notebook](https://github.com/bplabombarda/statsapiclient/blob/development/examples/examples.ipynb)\n",
    'author': 'Brett LaBombarda',
    'author_email': 'bplabombarda@gmail.com',
    'url': 'https://github.com/bplabombarda/statsapiclient',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
