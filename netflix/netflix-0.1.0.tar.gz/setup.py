# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['netflix']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.0', 'requests>=2.0']

setup_kwargs = {
    'name': 'netflix',
    'version': '0.1.0',
    'description': 'A Python client for Netflix.',
    'long_description': '# netflix\n\n[![Build Status](https://travis-ci.org/efe/netflix.svg?branch=master)](https://travis-ci.org/efe/netflix) [![pypi](https://img.shields.io/pypi/v/netflix.svg)](https://pypi.org/project/netflix/)\n\nA Python client for Netflix.\n\n## Installation\n\n```\npip install netflix\n```\n\n## Documentation\n\n### Netflix ID\n\n- **Movie**: The Intern\n- **URL**: `https://www.netflix.com/watch/80047616`\n- **Netflix ID**: `80047616`\n\n### Movie\n\n```python\nfrom netflix import Movie\n\nmovie = Movie("80047616")\nprint(movie.name)  # \'The Intern\'\n```\n\n#### Attributes\n\n- `name`: `\'The Intern\'`\n- `genre`: `\'Comedies\'`\n- `description`: `\'Harried fashion entrepreneur Jules gets a surprise boost from Ben, a 70-year-old widower who answers an ad seeking a senior intern.\'`\n- `image_url`: `\'https://occ-0-2774-2773.1.nflxso.net/dnm/api/v6/6AYY37jfdO6hpXcMjf9Yu5cnmO0/AAAABW8TwHJmfYqEjUj0YK4Y2ugq-sKIN-Gi8OBaDjOh3SbRSBdbEXlmpWEpHTbrO2CLDdo7yxRl7MTm5YtYa1-71Kg1o-7o.jpg?r=2ce\'`\n- `metadata`\n\n### TVShow\n\n```python\nfrom netflix import TVShow\n\ntv_show = TVShow("80192098")\nprint(tv_show.name)  # \'Money Heist\'\n```\n\n#### Attributes\n\n- `name`: `\'Money Heist\'`\n- `genre`: `\'TV Thrillers\'`\n- `description`: `\'Eight thieves take hostages and lock themselves in the Royal Mint of Spain as a criminal mastermind manipulates the police to carry out his plan.\'`\n- `image_url`: `\'https://occ-0-2774-2773.1.nflxso.net/dnm/api/v6/6AYY37jfdO6hpXcMjf9Yu5cnmO0/AAAABRQ7vD9Tg2GJUxLlWRw85C9Ln3j_m3dMvVhpf-LAJLDg9JNVsQKRyqvwlH28uoYY_gW7ROp1CI1PYdkBIlJwxpB8_VzK.jpg?r=8f1\'`\n- `metadata`\n\n### Extra\n\n#### Fetch Instantly\n\nDefault is `True`\n\n```python\nfrom netflix import Movie\n\nmovie = Movie("80047616", fetch_instantly=False)\n\n# Do something.\n\nmovie.fetch()\n```\n\n#### Metadata\n\n```python\nfrom netflix import Movie\n\nmovie = Movie("80047616")\n\nprint(movie.metadata)\n"""\n{\n  \'@context\': \'http://schema.org\',\n  \'@type\': \'Movie\',\n  \'url\': \'https://www.netflix.com/tr-en/title/80047616\',\n  \'contentRating\': \'16+\',\n  \'name\': \'The Intern\',\n  \'description\': \'Harried fashion entrepreneur Jules gets a surprise boost from Ben, a 70-year-old widower who answers an ad seeking a senior intern.\',\n  \'genre\': \'Comedies\',\n  \'image\': \'https://occ-0-2773-2774.1.nflxso.net/dnm/api/v6/6AYY37jfdO6hpXcMjf9Yu5cnmO0/AAAABW8TwHJmfYqEjUj0YK4Y2ugq-sKIN-Gi8OBaDjOh3SbRSBdbEXlmpWEpHTbrO2CLDdo7yxRl7MTm5YtYa1-71Kg1o-7o.jpg?r=2ce\',\n  \'dateCreated\': \'2019-8-31\',\n  \'actors\': [{\n    \'@type\': \'Person\',\n    \'name\': \'Robert De Niro\'\n  }, {\n    \'@type\': \'Person\',\n    \'name\': \'Anne Hathaway\'\n  }, {\n    \'@type\': \'Person\',\n    \'name\': \'Rene Russo\'\n  }, {\n    \'@type\': \'Person\',\n    \'name\': \'Anders Holm\'\n  }, {\n    \'@type\': \'Person\',\n    \'name\': \'JoJo Kushner\'\n  }, {\n    \'@type\': \'Person\',\n    \'name\': \'Andrew Rannells\'\n  }, {\n    \'@type\': \'Person\',\n    \'name\': \'Adam Devine\'\n  }, {\n    \'@type\': \'Person\',\n    \'name\': \'Zack Pearlman\'\n  }, {\n    \'@type\': \'Person\',\n    \'name\': \'Jason Orley\'\n  }, {\n    \'@type\': \'Person\',\n    \'name\': \'Christina Scherer\'\n  }],\n  \'creator\': [],\n  \'director\': [{\n    \'@type\': \'Person\',\n    \'name\': \'Nancy Meyers\'\n  }]\n}\n"""\n```\n',
    'author': 'Efe Öge',
    'author_email': 'efeoge@gmail.com',
    'url': 'https://github.com/efe/netflix',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=2.7',
}


setup(**setup_kwargs)
