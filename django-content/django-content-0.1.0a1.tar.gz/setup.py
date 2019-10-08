import os
import sys

from setuptools import find_packages, setup


CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 6)

BASE_DIR = os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir))

# Allow setup.py to be run from any path
os.chdir(BASE_DIR)

# Avoids IDE errors, but actual version is read from version.py
__version__ = None
with open(os.path.join(BASE_DIR, 'version.py')) as f:
    exec(f.read())

# Get the long description from README file
with open(os.path.join(BASE_DIR, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

EXCLUDE_FROM_PACKAGES = ['docs', 'contrib', 'tests', 'test_server', 'tools', 'scripts']

setup(
    name='django-content',
    version=__version__,
    python_requires='>={}.{}'.format(*REQUIRED_PYTHON),
    url='https://gitlab.com/Django.apps/django-content',
    author='a.Signz',
    author_email='a.Signz089@googlemail.com',
    description='Django Content framework.',
    long_description=long_description,
    license='BSD',
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    install_requires=['Django~=2.2'],
    extras_require={
        "dev": ['black==19.3b0', 'flake8~=3.7.8'],
        "test": [
            'pytest~=5.1',
            'pytest-cov~=2.7',
            'pytest-django~=3.5',
            'pytest-flake8~=1.0',
        ],
    },
    zip_safe=False,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
    ],
    project_urls={
        'Bug Reports': 'https://gitlab.com/Django.apps/django-content/issues',
        'Source': 'https://gitlab.com/Django.apps/django-content',
    },
)
