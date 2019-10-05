import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-dawa',
    version='0.1.0',
    packages=find_packages("src"),
    package_dir={'': 'src'},
    include_package_data=True,
    license='BSD License',
    description='Django app for using the dawa API, including models for replicating the address data from https://dawa.aws.dk',
    long_description=README,
    url='https://github.com/tykling/django-dawa',
    download_url='https://github.com/tykling/django-dawa/archive/v0.1.0.tar.gz',
    author='Thomas Steen Rasmussen',
    author_email='thomas@gibfest.dk',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'requests',
    ],
)
