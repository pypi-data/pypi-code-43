# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['rero']

package_data = \
{'': ['*']}

install_requires = \
['cobs>=1.1,<2.0', 'crcmod>=1.7,<2.0']

setup_kwargs = {
    'name': 'rero',
    'version': '1.0.1',
    'description': 'Rero is a transmission protocol suitable for efficient, reliable, and robust communication especially well suited for DMA supported MCU operations.',
    'long_description': "[![pipeline status](https://gitlab.com/PaniR/rero/badges/master/pipeline.svg)](https://gitlab.com/PaniR/rero/commits/master)\n[![coverage report](https://gitlab.com/PaniR/rero/badges/master/coverage.svg)](https://gitlab.com/PaniR/rero/commits/master)\n[![PyPI version](https://badge.fury.io/py/rero.svg)](https://badge.fury.io/py/rero)\n\n*Rero* is an efficient communication protocol intended for transmissions of byte frames over e.g. a serial interface or buses.\nIt builds upon [COBS](https://en.wikipedia.org/wiki/Consistent_Overhead_Byte_Stuffing) which allows for a minimum encoding overhead.\nIt is perfectly suited for MCUs with DMA support.\n\nDid somebody asked what is it good for? Here are some qualities of Rero:\n\n| Quality     | How                          | Good for                             |\n|-------------|------------------------------|--------------------------------------|\n| Reliable    | CRC check                    | Checking integrity of frame          |\n| Robust      | [COBS](https://en.wikipedia.org/wiki/Consistent_Overhead_Byte_Stuffing) and [COBSR](https://github.com/cmcqueen/cobs-c) byte stuffing           | Easy to resynchronize byte stream    |\n| Efficient   | Exploit properties of COBS and COBSR   | Minimum processing overhead          |\n| Scalable    | Customize Rero to your needs | Minimize frame overhead              |\n| Bus-capable | Optional address field       | Address frame for specific recipient |\n\nA C implementation written for STM32 MCUs is available [here](https://gitlab.com/PaniR/rero_stm32). It builds upon a very efficient ring buffer implementation tailored for UART interfaces, which of course utilizes DMA support for transmission and reception.\n\n## Quick start\n\nRero requires Python 3.5 or newer to run.\n\n```bash\n$ pip install rero\n```\n\n## Usage\n\n```python\nimport rero\n\nreroPacker = rero.Packer(1) \t# own address = 1\n\n# Dummy payload\npayload = bytes([1, 2, 3, 4])\n\nmsgToSend = reroPacker.pack(payload, 20) # Packing with dedicated address = 20\n\n# msgToSend may now be sent e.g. by use of pySerial...\n\n# Unpack received frame\nfor payloadRcd in reroPacker.unpack(msgToSend):\n\tprint(payloadRcd)\n```\n\t\nFurther examples are given in the [docs](https://panir.gitlab.io/rero).\n\n## Documentation\n\nYou can find the documentation at [here](https://panir.gitlab.io/rero).\n\n## Contribution\nFor information on how to contribute to the project, please check the [Contributor's Guide](CONTRIBUTING.md).\n\n## Contact\nPlease use the [Gitlab service desk](incoming+panir-rero-11417024-issue-@incoming.gitlab.com) or if you have a Gitlab account you may directly open an [issue](https://gitlab.com/PaniR/rero/issues).\n\n## License\n[MIT License](LICENSE)",
    'author': 'Reinhard Panhuber',
    'author_email': None,
    'url': 'https://panir.gitlab.io/rero',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
