# -*- coding: utf-8 -*-
from setuptools import setup


# do not forget to update sphinx_pynpoint_theme/__init__.py !
version= "0.1.7"


setup(
    name='sphinx-pynpoint-theme',
    version=version,
    license='MIT',
    description='ETH cosmology theme for Sphinx, 2013 version.',
    long_description=open('README.rst').read(),
    zip_safe=False,
    packages=['sphinx_pynpoint_theme'],
    package_data={'sphinx_pynpoint_theme': [
        'theme.conf',
        '*.html',
        'static/css/*.css',
        'static/js/*.js',
        'static/font/*.*'
    ]},
    include_package_data=True,
    install_requires=open('requirements.txt').read().splitlines(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
    ],
)
