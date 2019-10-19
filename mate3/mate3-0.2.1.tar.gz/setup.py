# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['mate3']

package_data = \
{'': ['*']}

install_requires = \
['pymodbus>=2.2,<3.0']

extras_require = \
{'mate3_pg': ['psycopg2>=2.8.3,<3.0.0', 'pyyaml>=5.1.2,<6.0.0']}

entry_points = \
{'console_scripts': ['mate3 = mate3.main:main',
                     'mate3_pg = mate3.mate3_pg:main']}

setup_kwargs = {
    'name': 'mate3',
    'version': '0.2.1',
    'description': '',
    'long_description': "# Outback Mate 3 Python Library\n\nThis library provides complete support for all outback devices (at least in theory, \nI don't own all the devices so cannot test it).\n\nThis data is accessed though the Mate3's Modbus interface.\n\nTested on Python 3.7. May work on 3.6.\n\n## Enabling the Modbus interface on your Mate 3\n\nTBA. System -> opticsre -> Modbus?\n\n## Using the library\n\nExample use:\n\n```python\nfrom mate3 import mate3_connection\nimport time\n\nhost = '192.168.0.123'\nport = 502\n\nwith mate3_connection(host, port) as client:\n    while True:\n        for block in client.all_blocks():\n            print(block)\n\n        time.sleep(3)\n```\n\n## Using the command line interface (CLI)\n\nA simple CLI is available which will read all available values from the Mate3:\n\n```\n$ mate3 -h\nusage: mate3 [-h] [--host HOST] [--port PORT]\n             [--format {text,prettyjson,json}]\n\nRead all available data from the Mate3 controller\n\noptional arguments:\n  -h, --help            show this help message and exit\n  --host HOST, -H HOST  The host name or IP address of the Mate3\n  --port PORT, -p PORT  The port number address of the Mate3\n  --format {text,prettyjson,json}, -f {text,prettyjson,json}\n                        Output format\n```\n\nExample use:\n\n```\n$ mate3 --host 192.168.0.123\n```\n\n## Various notes\n\nThe `structures.py` and `parsers.py` files are *auto generated* \nfrom the CSV files located in `registry_data/`. The CSV files are \ngenerated though text extraction from the \n[axs_app_note.pdf](http://www.outbackpower.com/downloads/documents/appnotes/axs_app_note.pdf) \nPDF provided by OutBack. This process is handled by two python files:\n\n* `csv_generator.py` – Extract the CSV data from the PDF\n* `code_generator.py` – Generate the Python code from the CSV data\n\n## Future work\n\n* Support the writing of values back to the Mate3\n* Web interface?\n\n## Credits\n\nThis is a heavily refactored version of \n[basrijn's Outback_Mate3 library](https://github.com/basrijn/Outback_Mate3).\nThank you basrijn!\n",
    'author': 'Adam Charnock',
    'author_email': 'adam@adamcharnock.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
