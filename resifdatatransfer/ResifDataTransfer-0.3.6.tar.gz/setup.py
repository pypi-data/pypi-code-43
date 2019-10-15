import sys
from setuptools import find_packages, setup

assert sys.version_info >= (3, 5, 0), "ResifDataTransfer requires Python 3.5+"

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = ["ResifDataTransferTransaction"]

setup(
    name="ResifDataTransfer",
    version="0.3.6",
    author="RESIF",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    long_description=long_description,
    long_description_content_type="text/markdown; charset=UTF-8",
    data_files=[("resif_data_transfer/", ["ResifDataTransfer/ResifDataTransfer.conf.dist"])],
    url='https://gitlab.com/resif/resif-data-transfer',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.5",
    entry_points={
        'console_scripts': [
            'ResifDataTransfer=ResifDataTransfer.__main__:main',
        ],
    },
)
