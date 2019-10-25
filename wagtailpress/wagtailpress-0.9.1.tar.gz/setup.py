#!/usr/bin/env python3
from setuptools import setup, find_packages
import wagtailpress


package = 'wagtailpress'
version = wagtailpress.version
url = 'https://framagit.org/SebGen/wagtailpress'
author = "Sébastien Gendre"
author_email = 'seb@k-7.ch'
license = 'LGPLv3'

setup(
    name=package,
    version=version,
    url=url,
    description=wagtailpress.description,
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author=author,
    author_email=author_email,
    license=license,
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Framework :: Django',
        'Framework :: Wagtail',
        'Framework :: Wagtail :: 2',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='wagtailpress wagtail press blog',
    python_requires='>=3',
    install_requires=open('requirements.txt').read(),
)
