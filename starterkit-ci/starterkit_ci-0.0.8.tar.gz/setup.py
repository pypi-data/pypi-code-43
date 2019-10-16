from setuptools import setup, find_packages
import os
from os.path import abspath, dirname, join
from io import open

here = abspath(dirname(__file__))

# Get the long description from the README file
with open(join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

package_data = []
for root, dirs, files in os.walk(join(here, 'src/starterkit_ci/sphinx_config/_static')):
    package_data += [join(root, fn) for fn in files]

setup(
    name='starterkit_ci',
    use_scm_version=True,
    description='Helpers for Starterkit Continuous Integration',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/lhcb/starterkit_ci',

    author='LHCb Starterkit',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='Starterkit',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    python_requires='>=3.6',
    setup_requires=['setuptools_scm'],
    install_requires=[
        'sphinx',
        'sphinx-rtd-theme',
        'recommonmark',
        'nbsphinx',
    ],
    package_data={
        'starterkit_ci': package_data,
    },
    zip_safe=False,
    entry_points={
        'console_scripts': {
            'starterkit_ci = starterkit_ci:parse_args',
        }
    },
    project_urls={
        'Bug Reports': 'https://github.com/lhcb/starterkit_ci/issues',
        'Source': 'https://github.com/lhcb/starterkit_ci',
    },
)
