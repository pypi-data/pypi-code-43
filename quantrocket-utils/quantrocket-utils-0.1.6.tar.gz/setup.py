# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['quantrocket_utils']

package_data = \
{'': ['*']}

install_requires = \
['arrow>=0.15.2,<0.16.0',
 'colorama>=0.4.1,<0.5.0',
 'ib-trading-calendars>=0.1.2,<0.2.0',
 'termcolor>=1.1,<2.0',
 'trading-calendars>=1.10,<2.0']

setup_kwargs = {
    'name': 'quantrocket-utils',
    'version': '0.1.6',
    'description': 'Utility methods for common tasks in QuantRocket.',
    'long_description': '# QuantRocket Utility Library\nUtility methods for common tasks in QuantRocket.\n\n## Installation\n`quantrocket-utils` can be installed via `pip`:\n```bash\n$ pip install quantrocket-utils\n```\n\n## Development\n\nThis project uses [poetry](https://poetry.eustace.io/) for development and release management.\n```\n$ git clone git@github.com:boosting-alpha-bv/quantrocket-utils.git\n$ cd quantrocket-utils/\n$ poetry install\n```\n\n### Running Tests\n```bash\n$ poetry run coverage run --branch --source quantrocket_utils -m pytest\n```\n\n### Generating Coverage Reports\n```bash\n$ poetry run coverage html\n```\n\n### Running flake8\n```bash\n$ poetry run flake8 quantrocket_utils tests\n```\n\n### Deploying\n```bash\n$ poetry publish --build --username "${PYPI_USERNAME}" --password "${PYPI_PASSWORD}" --no-interaction\n```\n\n## Usage\nThis library requires an external file that contains the listing information for the stocks it should translate.\nThis is typically exported from QuantRocket and then supplied at initialization time of the library.\nWork is currently under way to remove the dependency on QuantRocket for obtaining this listings file.\n\n```python\n# Import the library and initialize the ConID resolution\nfrom quantrocket_utils import initialize as assets_init, Asset\nassets_init("<path>/<to>/listings.csv")\n\n# Create an Asset using the symbol name\nspy = Asset("SPY")\n# The exchange is optional, unless two symbols of the same name exist on different exchanges\nspy = Asset("SPY", "ARCA")\n\n# Create an Asset using the ConID\n# In this case the exchange can be inferred from the ConID, so it is always otpional\nspy = Asset(756733)\n# ConID\'s can be strings as well, so don\'t worry about type conversion\nspy = Asset("756733")\n\n# Access data on the object\nspy.conid\n>> 756733\nspy.symbol\n>> "SPY"\nspy.exchange\n>> "ARCA"\n\n# Check trading times\nspy.can_trade("2019-03-04", "10:34:02")\n>> True\n\n# Assets also support equality and comparison operations based on the ConID\n# However, this is mostly just useful for guaranteeing sorting order\n# Assets are also hashable and can thus be utilized in set operations\nAsset("SPY") < Asset("AAPL")\n>> True\n```\n',
    'author': 'Tim Wedde',
    'author_email': 'timwedde@icloud.com',
    'url': 'https://github.com/boosting-alpha-bv/quantrocket-utils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
