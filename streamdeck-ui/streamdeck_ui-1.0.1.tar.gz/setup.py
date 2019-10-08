# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['streamdeck_ui']

package_data = \
{'': ['*'], 'streamdeck_ui': ['fonts/roboto/*']}

install_requires = \
['hidapi>=0.7.99,<0.8.0',
 'pillow>=6.1,<7.0',
 'pynput>=1.4,<2.0',
 'pyside2>=5.13,<6.0',
 'streamdeck>=0.5.0,<0.6.0']

entry_points = \
{'console_scripts': ['streamdeck = streamdeck_ui.gui:start']}

setup_kwargs = {
    'name': 'streamdeck-ui',
    'version': '1.0.1',
    'description': 'A service, Web Interface, and UI for interacting with your computer using a Stream Deck',
    'long_description': '[![streamdeck_ui - Linux compatible UI for the Elgato Stream Deck](https://raw.githubusercontent.com/timothycrosley/streamdeck-ui/master/art/logo_large.png)](https://timothycrosley.github.io/streamdeck-ui/)\n_________________\n\n[![PyPI version](https://badge.fury.io/py/streamdeck-ui.svg)](http://badge.fury.io/py/streamdeck-ui)\n[![Build Status](https://travis-ci.org/timothycrosley/streamdeck-ui.svg?branch=master)](https://travis-ci.org/timothycrosley/streamdeck-ui)\n[![codecov](https://codecov.io/gh/timothycrosley/streamdeck-ui/branch/master/graph/badge.svg)](https://codecov.io/gh/timothycrosley/streamdeck-ui)\n[![Join the chat at https://gitter.im/timothycrosley/streamdeck-ui](https://badges.gitter.im/timothycrosley/streamdeck-ui.svg)](https://gitter.im/timothycrosley/streamdeck-ui?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)\n[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://pypi.python.org/pypi/streamdeck-ui/)\n[![Downloads](https://pepy.tech/badge/streamdeck-ui)](https://pepy.tech/project/streamdeck-ui)\n_________________\n\n[Read Latest Documentation](https://timothycrosley.github.io/streamdeck-ui/) - [Browse GitHub Code Repository](https://github.com/timothycrosley/streamdeck-ui/)\n_________________\n\n**streamdeck_ui** A Linux compatible UI for the Elgato Stream Deck.\n\n![Streamdeck UI Usage Example](https://raw.github.com/timothycrosley/streamdeck-ui/master/art/example.gif)\n\n## Key Features\n\n* **Linux Compatible**: Enables usage of all Stream Deck devices on Linux without needing to code.\n* **Multi-device**: Enables connecting and configuring multiple Stream Deck devices on one computer.\n* **Brightness Control**: Supports controlling the brightness from both the configuration UI and buttons on the device itself.\n* **Configurable Button Display**: Icons + Text, Icon Only, and Text Only configurable per button on the Stream Deck.\n* **Multi-Action Support**: Run commands, write text and press hotkey combinations at the press of a single button on your Stream Deck.\n* **Button Pages**: streamdeck_ui supports multiple pages of buttons and dynamically setting up buttons to switch between those pages.\n* **Auto Reconnect**: Automatically and gracefully reconnects, in the case the device is unplugged and replugged in.\n* **Import/Export**: Supports saving and restoring Stream Deck configuration.\n\nCommunication with the Streamdeck is powered by the [Python Elgato Stream Deck Library](https://github.com/abcminiuser/python-elgato-streamdeck#python-elgato-stream-deck-library).\n\n## Linux Quick Start\n\nTo use streamdeck_ui on Linux, you will need first to install some pre-requisite system libraries and give your user access to the Stream Deck devices.\n\n[Here](https://github.com/timothycrosley/streamdeck-ui/blob/master/scripts/ubuntu_install.sh) is a simple script for doing that on Ubuntu:\n\n```bash\n#!/bin/bash -xe\n\nsudo apt install libhidapi-hidraw0 libudev-dev libusb-1.0-0-dev\n\nsudo usermod -a -G plugdev `whoami`\n\nsudo tee /etc/udev/rules.d/99-streamdeck.rules << EOF\nSUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTRS{idProduct}=="0060", MODE:="666", GROUP="plugdev"\nSUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTRS{idProduct}=="0063", MODE:="666", GROUP="plugdev"\nSUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTRS{idProduct}=="006c", MODE:="666", GROUP="plugdev"\nEOF\n\nsudo udevadm control --reload-rules\n\necho "Unplug and replug in device for the new udev rules to take effect"\n```\n\nAs mentioned in the echo in the last line, make sure you unplug and replug your device before continuing.\nOnce complete, you should be able to install streamdeck_ui:\n\n```bash\nsudo pip3 install streamdeck_ui\n```\n\nYou can then launch `streamdeck` to start configuring your device.\n\n```bash\nstreamdeck\n```\n\nIt\'s recommended that you include `streamdeck` in your windowing environment\'s list of applications to auto-start.\n\n## Generic Quick Start\n\nOn other Operating Systems, or if you already have the required libraries and permissions, you should be able to install and run streamdeck_ui:\n\n```bash\npip3 install streamdeck_ui --user\nstreamdeck\n```\n',
    'author': 'Timothy Crosley',
    'author_email': 'timothy.crosley@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
