# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages
from shutil import copy2

with open("README.md", "r") as fh:
    long_description = fh.read()

setup_args = {
    'name': 'ndx-ecog',
    'version': '0.1.1',
    'description': 'An NWB extension for storing the cortical surface of subjects in ECoG experiments',
    'author': 'Ben Dichter',
    'author_email': 'ben.dichter@gmail.com',
    'url': '',
    'long_description': long_description,
    'long_description_content_type': "text/markdown",
    'license': 'BSD 3-Clause',
    'install_requires': [
        'pynwb>=1.1.2'
    ],
    'packages': find_packages('src/pynwb'),
    'package_dir': {'': 'src/pynwb'},
    'package_data': {'ndx_ecog': [
        'spec/ndx-ecog.namespace.yaml',
        'spec/ndx-ecog.extensions.yaml',
    ]},
    'classifiers': [
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
    'zip_safe': False
}


def _copy_spec_files(project_dir):
    ns_path = os.path.join(project_dir, 'spec', 'ndx-ecog.namespace.yaml')
    ext_path = os.path.join(project_dir, 'spec', 'ndx-ecog.extensions.yaml')

    dst_dir = os.path.join(project_dir, 'src', 'pynwb', 'ndx_ecog', 'spec')
    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir)

    copy2(ns_path, dst_dir)
    copy2(ext_path, dst_dir)


if __name__ == '__main__':
    _copy_spec_files(os.path.dirname(__file__))
    setup(**setup_args)
