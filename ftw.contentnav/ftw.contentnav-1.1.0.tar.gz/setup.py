from setuptools import setup, find_packages
import os

version = '1.1.0'

tests_require = [
    'ftw.builder',
    'ftw.testing',
    'ftw.testbrowser',
    'plone.app.testing',
    ]

extras_require = {
    'tests': tests_require,
    'test': tests_require,
    }

setup(name='ftw.contentnav',
      version=version,
      description='''
          Provides a content navigation behavior,
          which allows you to show sub content by category.''',
      long_description=open('README.rst').read() + '\n' +
                  open(os.path.join('docs', 'HISTORY.txt')).read(),

      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Framework :: Plone',
          'Framework :: Plone :: 4.3',
          'Framework :: Plone :: 5.1',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],

      keywords='ftw plone contentnav subcontent',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.contentnav',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', ],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
          'setuptools',
          'ftw.profilehook',
          'ftw.upgrade',
          'plone.api',
          'plone.behavior',
          'plone.dexterity',
          'plone.app.dexterity',
          'plone.app.widgets',
          'plone.directives.form',
          ],

      tests_require=tests_require,
      extras_require=extras_require,

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
