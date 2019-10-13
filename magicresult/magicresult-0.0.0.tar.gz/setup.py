"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from setuptools.command.install import install as _install
from setuptools.command.develop import develop as _develop
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

from post_setup import main as post_install

class CustomInstall(_install):
    def run(self):
        _install.run(self)
        post_install()

class CustomDevelop(_develop):
    def run(self):
        _develop.run(self)
        post_install()

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

if __name__ == '__main__':
    setup(
        name='magicresult',

        # Versions should comply with PEP440.  For a discussion on single-sourcing
        # the version across setup.py and the project code, see
        # https://packaging.python.org/en/latest/single_source_version.html
        version='0.0.0',

        description='Module providing magic result types via Python macros',
        long_description=long_description,
        long_description_content_type='text/markdown',

        # The project's main homepage.
        url='https://github.com/ddworken/magicresult',

        # Author details
        author='David Dworken',
        author_email='david@daviddworken.com',

        # Choose your license
        license='MIT',

        # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
        classifiers=[
            'Development Status :: 3 - Alpha',

            # Indicate who your project is intended for
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Build Tools',

            # Pick your license as you wish (should match "license" above)
            'License :: OSI Approved :: MIT License',

            # Specify the Python versions you support here. In particular, ensure
            # that you indicate whether you support Python 2, Python 3 or both.
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
        ],

        # What does your project relate to?
        keywords='macro magic bad-ideas',

        # You can just specify the packages manually here if your project is
        # simple. Or you can use find_packages().
        # packages=find_packages(exclude=['contrib', 'docs', 'tests']),
        packages=find_packages(),

        # List run-time dependencies here.  These will be installed by pip when
        # your project is installed. For an analysis of "install_requires" vs pip's
        # requirements files see:
        # https://packaging.python.org/en/latest/requirements.html
        install_requires=['astor'],

        cmdclass={
            'install': CustomInstall,
            'develop': CustomDevelop,
        },
    )
