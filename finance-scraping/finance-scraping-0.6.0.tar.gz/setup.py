import os
from setuptools import setup

__version__ = '0.6.0'

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name='finance-scraping',
    packages=['finance_scraping'],
    package_data={
        'finance_scraping': ['scripts/configure.sh']
    },
    entry_points={
        'console_scripts': ['finance-scraper=finance_scraping.main:main']
    },
    version=__version__,
    description='Finance Scraping ETL Pipeline',
    long_description=long_description,
    url='https://github.com/jschnab/finance-scraping',
    author='Jonathan Schnabel',
    author_email='jonathan.schnabel31@gmail.com',
    license='GNU General Public License v3.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3.6.8',
    keywords='security web scraping etl database',
    install_requires=[
        'beautifulsoup4==4.7.1',
        'boto3==1.9.210',
        'psycopg2==2.8.3',
        'requests==2.22.0',
        'responses==0.10.6'
    ]
)
