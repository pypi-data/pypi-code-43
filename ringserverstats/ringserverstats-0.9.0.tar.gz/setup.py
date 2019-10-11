from io import open
from setuptools import setup, find_packages

with open('ringserverstats/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.0.1'

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='ringserverstats',
    version=version,
    description='Export logs from ringserver as influxdb timeseries',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Jonathan Schaeffer',
    author_email='jonathan.schaeffer@univ-grenoble-alpes.fr',
    maintainer='Jonathan Schaeffer',
    maintainer_email='jonathan.schaeffer@univ-grenoble-alpes.fr',
    url='https://github.com/resif/ringserver-stats',
    license='GPL-3.0',
    packages=find_packages(),
    install_requires=[
        'Click==7.0',
        'influxdb==5.2.1',
        'maxminddb==1.4.1',
        'maxminddb-geolite2==2018.703',
        'regex==2019.2.7',
        'geohash2'
    ],
    keywords=[
        '',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',

    ],

    tests_require=['coverage', 'pytest'],
    entry_points='''
    [console_scripts]
    ringserverstats=ringserverstats:cli
    '''
)
