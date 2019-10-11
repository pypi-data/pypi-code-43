from codecs import open
from os.path import abspath, dirname, join
from setuptools import setup, find_packages
from jootranslate import __version__, __author__


this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.rst'), encoding='utf-8') as file:
    long_description = file.read()

setup(
    name='jootranslate',
    version=__version__,
    description='cli tool to generate translation files for joomla',
    long_description=long_description,
    url='https://github.com/pfitzer/jtranslate.git',
    author=__author__,
    author_email='michael@mp-development.de',
    license='MIT',
    keywords='joomla cli translations',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    install_requires=['configobj'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'jootranslate=jootranslate.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Localization'
    ]
)
