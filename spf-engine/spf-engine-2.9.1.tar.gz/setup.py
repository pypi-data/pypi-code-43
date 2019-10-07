from setuptools import setup
import os
import sys

DESC = """SPF (Sender Policy Framework) processing engine for Postfix policy server and Milter implemented in Python."""

setup(name='spf-engine',
    version='2.9.1',
    description='SPF processing for Postfix (and Sendmail)',
    long_description=DESC,
    author='Scott Kitterman',
    author_email='scott@kitterman.com',
    url='https://launchpad.net/spf-engine',
    packages=['spf_engine'],
    keywords = ['Postfix', 'Sendmail', 'milter','spf','email'],
    zip_safe = False,
    install_requires = ['pyspf',],
    extras_require={'milter':  ['pymilter', 'authres',],
    },
    entry_points = {
        'console_scripts' : [
            'policyd-spf = spf_engine.policyd_spf:main',
            'pyspf-milter = spf_engine.milter_spf:main',
        ]},
    include_package_data=True,
    data_files=[(os.path.join('share', 'man', 'man1'),
        ['policyd-spf.1']), (os.path.join('share', 'man', 'man5'),
        ['policyd-spf.conf.5']), (os.path.join('etc', 'python-policyd-spf'),
        ['policyd-spf.conf']), (os.path.join('share', 'man', 'man5'),
        ['policyd-spf.peruser.5']), (os.path.join('lib', 'systemd', 'system'),
        ['system/pyspf-milter.service']),(os.path.join('etc', 'init.d'),
        ['system/pyspf-milter']) ],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Topic :: Communications :: Email :: Mail Transport Agents',
        'Topic :: Communications :: Email :: Filters',
    ]
)

if sys.version_info < (3, 3):
    raise Exception("SPF engine requires python3.3 and later.")
