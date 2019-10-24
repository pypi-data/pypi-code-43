"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

from os import path

import setuptools

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='bazel-workspaces-python',
    version='0.1.0',
    description='Generator of Bazel workspaces for Python modules',
    url='https://github.com/kubic-project/bazel-workspaces-python',
    author='Michal Rostecki',
    author_email='mrostecki@opensuse.org',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='bazel build workspaces',
    packages=setuptools.find_packages(exclude=['contrib', 'docs', 'tests']),
    python_requires='>=3.6.*, <4',
    install_requires=[],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage', 'pytest'],
    },
    entry_points={
        'console_scripts': [
            'bazel-workspace-python=bazel_workspaces_python.cli:main',
        ],
    },
)
