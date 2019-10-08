import os

from setuptools import setup, find_packages

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PKG_NAME = 'base-package'

# Avoids IDE errors, but actual version is read from version.py
__version__ = None
with open(os.path.join(BASE_DIR, '%s/version.py' % PKG_NAME.replace('-', '_'))) as f:
    exec(f.read())

# Get the long description from README file
with open(os.path.join(BASE_DIR, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

dev_requires = ['black==19.3b0', 'flake8~=3.7']

tests_requires = ['pytest~=5.1', 'pytest-cov~=2.7', 'pytest-flake8~=1.0']

install_requires = ['coloredlogs~=10.0', 'humanfriendly~=4.18']

extras_requires = {
    'dev': dev_requires,
    'test': tests_requires,
    'docs': ['Sphinx~=2.1.2', 'recommonmark~=0.4.0'],
    'extra': []
}

setup(
    name=PKG_NAME,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries',
    ],
    packages=find_packages(exclude=['docs', 'contrib', 'tests', 'tools', 'scripts']),
    entry_points={'console_scripts': ['base-package=base_package.__main__:main']},
    version=__version__,
    install_requires=install_requires,
    tests_require=tests_requires,
    extras_require=extras_requires,
    include_package_data=True,
    description='python package template.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='a.Signz',
    author_email='a.Signz089@googlemail.com',
    maintainer='a.Signz',
    maintainer_email='a.Signz089@googlemail.com',
    license='BSD License',
    keywords='',
    url='https://gitlab.com/a.signz089/base-package',
    project_urls={
        'Bug Reports': 'https://gitlab.com/a.signz089/base-package/issues',
        'Source': 'https://gitlab.com/a.signz089/base-package.git',
    },
    # download_url='https://gitlab.com/a.signz089/base-package/archive/{}.tar.gz' ''.format(__version__),
)
