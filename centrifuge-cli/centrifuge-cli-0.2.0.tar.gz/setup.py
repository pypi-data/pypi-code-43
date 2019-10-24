# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['centrifuge_cli']

package_data = \
{'': ['*']}

install_requires = \
['Click>=7.0,<8.0',
 'dateparser>=0.7.2,<0.8.0',
 'pandas>=0.25.1,<0.26.0',
 'requests>=2.22,<3.0']

entry_points = \
{'console_scripts': ['centrifuge = centrifuge_cli.main:cli']}

setup_kwargs = {
    'name': 'centrifuge-cli',
    'version': '0.2.0',
    'description': "A command line utility for interacting with the Centrifuge Firmware Analysis Platform's REST API.",
    'long_description': 'centrifuge-cli: The official Python CLI for Centrifuge\n=======================================================\n\nCentrifuge is an automated firmware analysis platform. It allows users to upload\ntheir firmware images to be analyzed for various security issues. This utility\ngives users the ability to interact and automate tasks via the Centrifuge\nRESTful API.\n\nFeatures\n--------\n\n- Upload firmware\n- Delete firmware reports\n- Query firmware analysis results\n- Search for firmware uploads\n\nQuick Start\n-----------\n\nCheck your Python version (must be 3.6 or later):\n\n.. code-block:: bash\n\n    $ python --version\n\nTo install the Centrifuge CLI, simply:\n\n.. code-block:: bash\n\n    $ pip install centrifuge-cli\n\nConfigure your environment:\n\n.. code-block:: bash\n\n    $ export CENTRIFUGE_APIKEY=xxxx\n    $ export CENTRIFUGE_URL=https://centrifuge.refirmlabs.com # change this if you\'re single tenant or on-premise\n\nTo query the list of available reports:\n\n.. code-block:: bash\n\n    $ centrifuge reports list\n\nUnder the hood the Centrifuge CLI is using python Pandas data frames to report\nthe results to the user. Since the API is json, which has heirarchical structure\nto it, we have chosen to flatten all the results into a column/row format for\nviewing inside of a terminal or for importing into spreadsheets, etc. However\nthe cli can also output CSV, and the original json results. For example:\n\nCSV:\n\n.. code-block:: bash\n\n    $ centrifuge --outfmt=csv reports list\n\nJSON:\n\n.. code-block:: bash\n\n    $ centrifuge --outfmt=json reports list\n\nWhen generating the human-readable Pandas output or when genering CSV you have\nthe option of choosing which columns you wish to export. For example, to display\nonly the original filename and model number of the firmware that was uploaded: \n\n.. code-block:: bash\n\n    $ centrifuge -foriginalFilename -fdevice reports list\n\n\nUploading Firmware\n------------------\nUploading firmware to centrifuge is quite simple. All you need to do is supply\nmake/model/version and the file you want to upload:\n\n.. code-block:: bash\n\n    $ centrifuge upload --make=Linksys --model=E1200 --version=1.0.04 /path/to/FW_E1200_v1.0.04.001_US_20120307.bin\n\nSearching Through Firmware Uploads\n----------------------------------\n\nYou can search through the uploaded firmware for keywords in username, filename, make, model, etc:\n\n.. code-block:: bash\n\n    $ centrifuge reports search "Linksys"\n\nQuerying Report Results\n------------------------\n\nAll the following commands require access to what we refer to as a "UFID" or\nUpload File ID. This ID can be seen through the web interface, its also the last\npart of the URL when viewing a report, it is also the ``id`` field when running\nthe ``centrifuge reports list`` command above. It should also be noted that all of\nthese commands also support the ``--outfmt`` argument so you can export to CSV and\nto JSON. However be aware that these arguments are positional in nature, you\nmust supply the ``--outfmt`` argument between ``centrifuge`` and ``report`` on the\ncommand line or it will not be accepted. \n\nYou can see the available commands by viewing the help output:\n\n.. code-block:: bash\n\n  $ centrifuge report --help\n  Usage: centrifuge report [OPTIONS] COMMAND [ARGS]...\n\n  Options:\n    --ufid ID  Centrifuge report ID  [required]\n    --help     Show this message and exit.\n\n  Commands:\n    code-emulated\n    code-static\n    code-summary\n    crypto\n    delete\n    guardian\n    info\n    passhash\n    sbom\n\nGet basic information about the report (User, Make, Model, Version, filename, etc):\n\n.. code-block:: bash\n\n    $ centrifuge report --ufid=<REPORT_ID> info\n\nGet Guardian Results:\n\n.. code-block:: bash\n\n    $ centrifuge report --ufid=<REPORT_ID> guardian\n\nGet Password Hashes:\n\n.. code-block:: bash\n\n    $ centrifuge report --ufid=<REPORT_ID> passhash\n\nGet Crypto Keys:\n\n.. code-block:: bash\n\n    $ centrifuge report --ufid=<REPORT_ID> crypto\n\nGet SBOM Results:\n\n.. code-block:: bash\n\n    $ centrifuge report --ufid=<REPORT_ID> sbom\n\nThe code analysis section is a little bit more complicated, since the data is\nmore structured. To understand how to access this data you need to understand\nthat when we process a firmware we must extract it first, each time we extract a\nfilesystem or file container those groups of files are given an ``extraction ID``\nor ``EXID``. To get code analysis results for an individual file you must know the\n``EXID`` and the file\'s ``PATH`` within that EXID. Luckily there is a ``code-summary``\ncommand which will give you the data you need to find into the ``code-static`` and\n``code-emulated`` commands.\n \nGet a Summary of the Code Analysis:\n\n.. code-block:: bash\n\n    $ centrifuge report --ufid=<REPORT_ID> code-summary\n\nWhen looking at the results above from the ``code-summary`` command you need to\nrecord the ``exid`` and ``path`` (*NOT* ``fullPath``), to feed into the next two commands. \n\nGet static code analysis results:\n\n.. code-block:: bash\n\n    $ centrifuge report --ufid=<REPORT_ID> code-static --exid=<EXID> --path=<PATH>\n\n\nGet emulated code analysis results:\n\n.. code-block:: bash\n\n    $ centrifuge report --ufid=<REPORT_ID> code-emulated --exid=<EXID> --path=<PATH>\n\n\nDeleting Firmware Uploads\n-------------------------\n\nDeleting a previously uploaded firmware is an unrecoverable action. Unlike the\nweb interface the command line interface will not prompt you if you are sure.\nSo use this command carefully. \n\nTo delete a firmware:\n\n.. code-block:: bash\n\n    $ centrifuge report --ufid=<REPORT_ID> delete\n',
    'author': 'Peter Eacmen',
    'author_email': 'peacmen@refirmlabs.com',
    'url': 'https://www.refirmlabs.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
