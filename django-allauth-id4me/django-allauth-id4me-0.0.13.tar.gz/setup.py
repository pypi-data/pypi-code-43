#!/usr/bin/env python

from setuptools import setup

setup(name='django-allauth-id4me',
      version='0.0.13',
      description='Social provider for django-allauth - ID4me https://id4me.org',
      long_description_content_type="text/markdown",
      long_description=open('README.md').read(),
      author='Pawel Kowalik',
      author_email='pawel-kow@users.noreply.github.com',
      url='https://gitlab.com/ID4me/django-allauth-id4me',
      license='https://gitlab.com/ID4me/django-allauth-id4me/blob/master/LICENSE',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Environment :: Web Environment',
          'Topic :: Internet',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Framework :: Django',
          'Framework :: Django :: 1.11',
          'Framework :: Django :: 2.0',
          'Framework :: Django :: 2.1',
      ],
      packages=[
          'allauth_id4me',
          'allauth_id4me.migrations',
      ],
      package_data={'django-allauth-id4me': ['allauth_id4me/templates/id4me/*.html']},
      include_package_data=True,
      install_requires=[
          'id4me-rp-client >= 0.0.23',
          'Django >= 1.11.16',
          'django-allauth >= 0.38.0',
      ],
      )
