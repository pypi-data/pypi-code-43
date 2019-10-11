import os
from setuptools import setup, find_packages

install_requires = [
    'numpy',
    'shapely'
    ]

setup(
    name='subdivide',
    version="1.0.1",
    description="Subdivides lines by several methods.",
    license='MIT',
    author='Daven Quinn',
    author_email='code@davenquinn.com',
    maintainer='Daven Quinn',
    maintainer_email='code@davenquinn.com',
    url='https://github.com/davenquinn/subdivide',
    install_requires=install_requires,
    packages=find_packages(),
    package_dir={'subdivide':'subdivide'},
    classifiers=[
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
    ],
)
