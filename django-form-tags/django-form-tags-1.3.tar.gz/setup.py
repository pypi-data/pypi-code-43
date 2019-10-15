#!/usr/bin/env python

from setuptools import find_packages, setup


version = '1.3'

setup(
    name='django-form-tags',
    packages=find_packages(),
    version=version,
    description='Django templatetags to easily render fieldholders, '
                'fieldwrappers and fields.',
    long_description=open('README.rst').read(),
    author='Sven Groot (Mediamoose)',
    author_email='sven@mediamoose.nl',
    url='https://gitlab.com/mediamoose/django-form-tags/tree/v{}'.format(version),  # noqa
    download_url='https://gitlab.com/mediamoose/django-form-tags/repository/v{}/archive.tar.gz'.format(version),  # noqa
    include_package_data=True,
    install_requires=[
        'django>=1.11',
        'django-svg-templatetag>=1.0.1',
    ],
    license='MIT',
    zip_safe=False,
    keywords=['forms', 'templatetags', 'django'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
