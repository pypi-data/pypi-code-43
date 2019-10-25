# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['twisted_fate', 'twisted_fate.api_wrapper', 'twisted_fate.deck_coder']

package_data = \
{'': ['*'], 'twisted_fate': ['data/data/*']}

install_requires = \
['requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'twisted-fate',
    'version': '0.1.0',
    'description': 'An api wrapper around the Legends of Runterra Client API with deck encoder implementation',
    'long_description': '# twisted_fate\n\n\nA python api wrapper to for riot\'s Legends of Runterra client-api including a port of [Riot Games C# implementation of the deck encoder/decoder](https://github.com/RiotGames/LoRDeckCodes)\n\n# Install\n\n\n```\npip install twisted_fate\n```\n\n## Usage\n\n### Create Deck from deck code\n```python\nfrom twisted_fate import Deck\n\ndraven_deck = Deck.decode(("CEBAGAIDCQRSOCQBAQAQYDISDQTCOKBNGQAACAIBAMFQ")\n\n# results\nprint(deck.cards)\n#[\n#    Card(01NX020, Name: Draven, Cost: 3), \n#    Card(01NX035, Name: Draven\'s Biggest Fan, Cost: 1), \n#    Card(01NX039, Name: Vision, Cost: 3), \n#    Card(01PZ001, Name: Rummage, Cost: 1), \n#    Card(01PZ012, Name: Flame Chompers!, Cost: 2), \n#    Card(01PZ013, Name: Augmented Experimenter, Cost: 6), #    Card(01PZ018, Name: Academy Prodigy, Cost: 2), \n#    Card(01PZ028, Name: Jury-Rig, Cost: 1), \n#    Card(01PZ038, Name: Sump Dredger, Cost: 2), \n#    Card(01PZ039, Name: Get Excited!, Cost: 3), \n#    Card(01PZ040, Name: Jinx, Cost: 4), \n#    Card(01PZ045, Name: Zaunite Urchin, Cost: 1), \n#    Card(01PZ052, Name: Mystic Shot, Cost: 2), \n#    Card(01NX011, Name: Whirling Death, Cost: 3)\n# ]\n```\n### Create Deck from cards list, (in the format of a response from the client api)\n```python\nfrom twisted_fate import Deck\n# client api response\ndeck = {\n    "DeckCode":"CEBAGAIDCQRSOCQBAQAQYDISDQTCOKBNGQAACAIBAMFQ",\n    "CardsInDeck": {\n        "01NX020": 3,\n        "01NX035": 3,\n        "01NX039": 3,\n        "01PZ001": 3,\n        "01PZ012": 3,\n        "01PZ013": 3,\n        "01PZ018": 3,\n        "01PZ028": 3,\n        "01PZ038": 3,\n        "01PZ039": 3,\n        "01PZ040": 3,\n        "01PZ045": 3,\n        "01PZ052": 3,\n        "01NX011": 1,\n    },\n}\n\n\ndraven_deck = Deck(cards=deck["CardsInDeck"])\nprint(draven_deck.encode().deck_code)\n# result: CEBAGAIDCQRSOCQBAQAQYDISDQTCOKBNGQAACAIBAMFQ\n\n# or\n\nprint(draven_deck.to_deck_code())\n# result: CEBAGAIDCQRSOCQBAQAQYDISDQTCOKBNGQAACAIBAMFQ\n```\n\n\n## Client API Wrapper\ncomming soon...\n\n\n',
    'author': 'Anthony Keelan',
    'author_email': 'anthony.keelan@gmail.com',
    'url': 'https://github.com/Snowcola/runeterra',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
