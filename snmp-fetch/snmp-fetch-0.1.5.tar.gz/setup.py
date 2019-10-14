# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['snmp_fetch', 'snmp_fetch.fp']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.1,<20.0',
 'numpy>=1.16,<2.0',
 'pandas>=0.25,<0.26',
 'toolz>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'snmp-fetch',
    'version': '0.1.5',
    'description': 'An opinionated python SNMPv2 library built for rapid database ingestion.',
    'long_description': 'snmp-fetch\n==========\n\n|Version badge| |Python version badge| |PyPI format badge| |Build badge| |Coverage badge|\n\n.. |Version badge| image:: https://img.shields.io/pypi/v/snmp-fetch\n   :target: https://pypi.org/project/snmp-fetch/\n\n.. |Python version badge| image:: https://img.shields.io/pypi/pyversions/snmp-fetch\n   :alt: PyPI - Python Version\n   :target: https://pypi.org/project/snmp-fetch/\n  \n.. |PyPI format badge| image:: https://img.shields.io/pypi/format/snmp-fetch\n   :alt: PyPI - Format\n   :target: https://pypi.org/project/snmp-fetch/\n\n.. |Build badge| image:: https://travis-ci.org/higherorderfunctor/snmp-fetch.svg?branch=master\n   :target: https://travis-ci.org/higherorderfunctor/snmp-fetch\n\n.. |Coverage badge| image:: https://coveralls.io/repos/github/higherorderfunctor/snmp-fetch/badge.svg\n   :target: https://coveralls.io/github/higherorderfunctor/snmp-fetch\n\nAn opinionated python3.7 SNMPv2 library designed for rapid database ingestion.\n\nPrerequisites\n"""""""""""""\n\nSnmp-fetch is built for python 3.7 and c++17.  Building is currently only tested on gcc 8 and each release is only tested against the latest version of each prerequisite dependency.  The following prerequisites must be installed before adding snmp-fetch to your project.\n\nnet-snmp\n\'\'\'\'\'\'\'\'\n\nA recent version of net-snmp is required; testing has only been performed against net-snmp 5.8.\n\n.. code:: console\n\n   # perl bindings may be needed on RPM based systems\n   sudo yum install perl-devel\n\n   # compile and install net-snmp\n   wget https://sourceforge.net/projects/net-snmp/files/net-snmp/5.8/net-snmp-5.8.tar.gz/download -O net-snmp.tar.gz\n   tar xzfv net-snmp.tar.gz\n   cd net-snmp-5.8\n   ./configure --enable-ipv6 --with-defaults\n   make\n   sudo make install\n   cd .. && rm -rf net-snmp*\n   sudo ldconfig -v\n\nboost (headers only)\n\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\'\n\nBoost is a popular C++ library to reduce boilerplate.  Snmp-fetch makes use of some of the header only libraries.\n\n.. code:: console\n\n   wget https://dl.bintray.com/boostorg/release/1.71.0/source/boost_1_71_0.tar.gz\n   tar xzfv boost_1_71_0.tar.gz\n   sudo mv boost_1_71_0/boost /usr/local/include/\n   rm -rf boost_1_71_0*\n\npybind11\n\'\'\'\'\'\'\'\'\n\nPybind11 is a C++ wrapper around the Python C API to reduce boilerplate.  This is a header only library, but the test script will attempt to build a binary.\n\n.. code:: console\n\n   # install pytest in the user space for the test build\n   pip3.7 install --user pytest\n\n   # install cmake\n   wget https://github.com/Kitware/CMake/releases/download/v3.15.4/cmake-3.15.4-Linux-x86_64.sh\n   chmod a+x cmake-3.15.4-Linux-x86_64.sh\n   sudo ./cmake-3.15.4-Linux-x86_64.sh \\\n     --prefix=/usr/local/ \\\n     --exclude-subdir \\\n     --skip-license\n   rm cmake-3.15.4-Linux-x86_64.sh\n\n   # test and install pybind11\n   wget https://github.com/pybind/pybind11/archive/v2.4.2.tar.gz -O pybind11.tar.gz\n   tar -xvf pybind11.tar.gz\n   cd pybind11-2.4.2\n   mkdir -p build && cd build\n   cmake .. -DPYBIND11_CPP_STANDARD=-std=c++17 -DDOWNLOAD_CATCH=1\n   make check -j 4\n   sudo make install\n   cd ../../\n   rm -rf pybind11*\n\nInstallation\n""""""""""""\n\n.. code:: console\n\n   # poetry\n   poetry add snmp-fetch\n   # pip\n   pip install snmp-fetch\n\nDevelopment\n"""""""""""\n\n.. code:: console\n\n   # poetry must be installed\n   git clone ...\n   cd snmp-fetch\n   virtualenv -p python3.7 ENV\n   source ENV/bin/activate\n   poetry install\n   deactivate && source ENV/bin/activate  # refresh PATH\n\n   # fast fail testing\n   pytest --hypothesis-show-statistics -x --ff\n\n   # testing\n   coverage erase\n   pytest --cov --hypothesis-show-statistics\n   coverage html\n\n   # linting\n   poetry run pylint snmp_fetch tests\n   poetry run flake8 snmp_fetch tests\n   poetry run mypy -p snmp_fetch -p tests\n   poetry run bandit -r snmp_fetch\n   poetry run pytest -v --cov --hypothesis-show-statistics tests/\n\n   # clean up imports\n   isort -rc --atomic .\n\nKnown Limitations\n"""""""""""""""""\n\n- The library only supports SNMPv2 at this time.\n\n- `BULKGET_REQUEST` and `NEXT_REQUEST` will always perform a walk.\n\n- Walks will always end if the root of the oid runs past the requested oid.\n\n- Duplicate objects on the same host/request will be silently discarded.\n\n  - This includes the initial request; walks must be performed on an oid prior to the first desired.\n\n- NO_SUCH_INSTANCE, NO_SUCH_OBJECT, and END_OF_MIB_VIEW variable bindings are exposed as errors for handling by the client.\n',
    'author': 'Christopher Aubut',
    'author_email': 'christopher@aubut.me',
    'url': 'https://github.com/higherorderfunctor/snmp-fetch',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
