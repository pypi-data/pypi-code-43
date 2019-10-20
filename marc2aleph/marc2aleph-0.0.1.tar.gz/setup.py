import setuptools

from marc2aleph import __version__, __author__

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='marc2aleph',
    version=__version__,
    author=__author__,
    description='Conversion from MARC(2709) to Aleph sequential and vice-versa',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/turricula/marc2aleph',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
