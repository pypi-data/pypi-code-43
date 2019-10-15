import os

import sys
from setuptools import setup, find_packages

PATH = os.path.dirname(os.path.abspath(__file__))

install_requires = []


def read(*paths):
    return open(os.path.join(PATH, *paths), 'r', encoding='utf-8').read()


about = {}
exec(read('process_bar', '__version__.py'), about)

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload dist/*{}*'.format(about['__version__']))
    sys.exit()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=read('README.md'),
    url=about['__url__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    license=about['__license__'],
    keywords=about['__keywords__'],
    packages=find_packages(exclude=['docs', 'tests*', 'example']),
    install_requires=install_requires,
    python_requires='>=3',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

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
    ],
)
