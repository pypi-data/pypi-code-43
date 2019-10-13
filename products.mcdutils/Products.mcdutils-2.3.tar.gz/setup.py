from setuptools import find_packages
from setuptools import setup


readme = open('README.rst').read()
history = open('CHANGES.txt').read()
long_description = readme + '\n\n' + history

setup(name='Products.mcdutils',
      version='2.3',
      description=('A Zope product with memcached-backed ZCache and '
                   'Zope session implementations.'),
      long_description=long_description,
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Zope',
        'Framework :: Zope2',
        'Framework :: Zope :: 2',
        'Framework :: Zope :: 4',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP :: Session'],
      keywords='session memcache memcached Products',
      author='Tres Seaver and contributors',
      author_email='tseaver@palladion.com',
      maintainer='Jens Vagelpohl',
      maintainer_email='jens@netz.ooo',
      url='https://mcdutils.readthedocs.io',
      project_urls={
        'Documentation': 'https://mcdutils.readthedocs.io',
        'Issue Tracker': ('https://github.com/dataflake/Products.mcdutils'
                          '/issues'),
        'Sources': 'https://github.com/dataflake/Products.mcdutils',
      },
      license='ZPL 2.1',
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['Products'],
      zip_safe=False,
      python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
      install_requires=[
        'setuptools',
        'six',
        'python-memcached',
        'Zope2',
        ],
      extras_require={
        'docs': ['repoze.sphinx.autointerface', 'Sphinx'],
        },
      )
