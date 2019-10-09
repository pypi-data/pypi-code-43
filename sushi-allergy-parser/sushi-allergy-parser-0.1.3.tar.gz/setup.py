# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['sushi_allergy_parser']

package_data = \
{'': ['*']}

install_requires = \
['tabula-py>=1.4,<2.0']

setup_kwargs = {
    'name': 'sushi-allergy-parser',
    'version': '0.1.3',
    'description': 'sushi-allergy-parser is a parser for allergy infomation document of japanese conveyor-belt sushi chain. ',
    'long_description': "# sushi-allergy-parser\n\n`sushi-allergy-parser` is a parser for allergy infomation document of japanese conveyor-belt sushi chain. Currently, the following documents are supported.\n\n* スシロー (http://www3.akindo-sushiro.co.jp/pdf/menu/allergy.pdf)\n* くら寿司 (http://www.kura-corpo.co.jp/common/pdf/kura_allergen.pdf)\n\n\n## Requirements\n\n`sushi-allergy-parser` depends on [tabula-py](https://github.com/chezou/tabula-py), so you should install Java(7 or 8).\n\n## Installation\n\n```sh\n$ pip install sushi-allergy-parser\n```\n\n## Usage\n\n```python\n>>> from sushi_allergy_parser import SushiroAllergyParser\n>>> df = SushiroAllergyParser().parse()\n>>> type(df)\n<class 'pandas.core.frame.DataFrame'>\n>>> df\n    category       name          egg  ...      gelatin       sesame    cashewNut\n0        にぎり  合鴨ロースの煮込み  NOT_CONTAIN  ...  NOT_CONTAIN  NOT_CONTAIN  NOT_CONTAIN\n1        にぎり        赤えび  NOT_CONTAIN  ...  NOT_CONTAIN  NOT_CONTAIN  NOT_CONTAIN\n2        にぎり         あじ  NOT_CONTAIN  ...  NOT_CONTAIN  NOT_CONTAIN  NOT_CONTAIN\n3        にぎり  あじ(ネギ・生姜)  NOT_CONTAIN  ...  NOT_CONTAIN  NOT_CONTAIN  NOT_CONTAIN\n4        にぎり   穴子天ぷらにぎり  MAY_CONTAIN  ...  MAY_CONTAIN  MAY_CONTAIN  NOT_CONTAIN\n..       ...        ...          ...  ...          ...          ...          ...\n319      その他        天つゆ  NOT_CONTAIN  ...  MAY_CONTAIN  MAY_CONTAIN  NOT_CONTAIN\n320      その他       粉末緑茶  NOT_CONTAIN  ...  NOT_CONTAIN  NOT_CONTAIN  NOT_CONTAIN\n321      その他        ぽん酢  NOT_CONTAIN  ...  NOT_CONTAIN  MAY_CONTAIN  NOT_CONTAIN\n322      その他        わかめ  NOT_CONTAIN  ...  NOT_CONTAIN  NOT_CONTAIN  NOT_CONTAIN\n323      その他        わさび  MAY_CONTAIN  ...  MAY_CONTAIN  NOT_CONTAIN  NOT_CONTAIN\n```\n",
    'author': 't3yamoto',
    'author_email': '3yamoto.dev@gmail.com',
    'url': 'https://github.com/t3yamoto/sushi-allergy-parser',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
