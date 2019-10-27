#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import os
from distutils.core import setup


def read(fname):
    return io.open(
        os.path.join(os.path.dirname(__file__), fname),
        'r', encoding='utf-8').read()


setup(name='tardis',
    version='0.1',
    author='Cédric Krier',
    author_email='cedric.krier@b2ck.com',
    url="http://bitbucket.org/cedk/tardis",
    description="A minimal CalDAV client",
    long_description=read('README'),
    download_url="http://bitbucket.org/cedk/tardis/downloads",
    packages=['tardis'],
    package_data={
        'tardis': ['tardis.png'],
        },
    classifiers=[
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later '
        '(GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Office/Business :: Scheduling',
        ],
    license='GPL-3',
    python_requires='>=3.4',
    install_requires=[
        # 'pygtk',
        # 'goocanvas',
        'GooCalendar>=0.5',
        'python-dateutil',
        'caldav',
        'vobject',
        ],
    entry_points="""
    [console_scripts]
    tardis = tardis:main
    """
    )
