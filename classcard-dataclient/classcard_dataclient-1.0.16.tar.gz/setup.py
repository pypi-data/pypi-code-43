import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md'), "r", encoding='utf-8') as fh:
    LONG_DESCRIPTION = fh.read()

DESCRIPTION = (
    'data client of class card server'
)
CLASSIFIERS = [
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6'
]
KEYWORDS = (
    'classcard data-client'
)

setup(
    name='classcard_dataclient',
    version='1.0.16',
    maintainer='Murray',
    maintainer_email='ma.yawei@h3c.com',
    url='http://gitlab.h3c.com/edtech/openconnection',
    download_url='http://gitlab.h3c.com/edtech/openconnection',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license='MIT',
    platforms='Platform Independent',
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    python_requires=">=3.5",
    install_requires=[
        'requests==2.22.0',
    ],
)
