"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='package-uploader',

    use_scm_version=True,

    description='Python Package Uploader - designed to upload your built packages to any non-standard repository',
    long_description=long_description,
    long_description_content_type="text/x-rst",

    url='https://github.com/gbdlin/package-uploader',

    author='GwynBleidD',
    author_email='gbd.lin@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',

        'Environment :: Web Environment',

        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',

        'License :: OSI Approved :: MIT License',

        'Operating System :: OS Independent',

        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords='django admin toolbox sidebar tools improvements',

    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'tools']),

    python_requires=">=3.6, <4",

    install_requires=[
        'six',
        'colorama',
        'pyyaml',
        'pysftp',
    ],

    extras_require={
    },

    setup_requires=[
        'setuptools_scm',
    ],

    include_package_data=True,

    entry_points={
        'console_scripts': [
            'upload-package=package_uploader.__main__:main',
        ],
    },
)
