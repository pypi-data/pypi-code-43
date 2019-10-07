from setuptools import setup
import os



setup(
    name         = 'hgflow-official',
    version      = '0.9.8.4',
    author       = 'Yujie Wu',
    author_email = 'yujie.wu2@gmail.com',
    url          = 'https://hg.sr.ht/~wu/hgflow',
    description  = 'Mercurial plugin to support the generalized Driessen branching model',
    package_dir  = {'hgext': 'src'},
    packages     = ['hgext'],
    license      = 'GPLv2',
    classifiers  = [
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Topic :: Software Development :: Version Control',
    ]
)
