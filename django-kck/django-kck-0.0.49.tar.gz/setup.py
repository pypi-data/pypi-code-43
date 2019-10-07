"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
from version import VERSION

# Get the long description from the README file
with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-kck',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=VERSION,

    description='Data orchestration for Django',
    long_description=long_description,
    long_description_content_type="text/markdown",

    # The project's main homepage.
    url='https://gitlab.com/frameworklabs/django-kck',

    # Author details
    author='Framework Labs',
    author_email='fred@frameworklabs.us',

    # Choose your license
    license='BSD',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='data orchestration framework',
    packages=[
        'django_kck'
    ],
    include_package_data=True,
    package_dir={'django_kck': 'django_kck'},
    install_requires=[
        "Django>=2.0.0",
        "python-dateutil>=2.2",
        "django-postgres-extensions>=0.9.3",
        "psycopg2-binary>=2.7.6.1",
        "django-picklefield==2.0"
    ],
    extras_require={},
    package_data={},
    data_files=["README.md"],
    entry_points={
        'console_scripts': [
        ]
    }
)
