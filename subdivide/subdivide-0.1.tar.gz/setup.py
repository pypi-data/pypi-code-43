import os
from setuptools import setup, find_packages

install_requires = [
    'numpy',
    'shapely'
    ]

setup(
    name='subdivide',
    version=0.1,
    description="Subdivides lines by several methods.",
    license='MIT',
    install_requires=install_requires,
    packages=find_packages(),
    package_dir={'subdivide':'subdivide'},
)
