# from distutils.core import setup
import GNOMEAcquirerLibs.Meta
import os
from setuptools import setup

try:
    del os.link
except:
    pass

includefiles = ["GNOMEAcquirerLibs/icon.png",
                "GNOMEAcquirerLibs/icon-with-debug.ico",
                "GNOMEAcquirerLibs/LogFile.png"]

setup(
    name="gnomeacquirer",
    version = GNOMEAcquirerLibs.Meta.__version__,
    author="Samer Afach",
    author_email="samer@afach.de",
    packages=["GNOMEAcquirerLibs","gnomedata"],
    include_package_data=True,
    url="https://git.afach.de/budker/GNOMEBoxDataAcquisition",
    description="GNOME experiment acquisition software for magnetometers",
    data_files=includefiles,
    #install_requires=['numpy', 'sympy', 'pyserial', 'pyqt', 'h5py', 'matplotlib'],
    python_requires = '>=3.4',
    entry_points={
        'console_scripts': [
            'gnomeacquirer = GNOMEAcquirerLibs.gnomeacquirer:main_function'
        ]},
    scripts=["gnomeacquirer_prepare.bat"]
)
