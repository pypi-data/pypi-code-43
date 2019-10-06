"""AoC QQ setup."""
from setuptools import setup, find_packages

setup(
    name='python-aoc-qq',
    version='1.0.1',
    description='AoC QQ API',
    url='https://github.com/happyleavesaoc/python-aoc-qq/',
    license='MIT',
    author='happyleaves',
    author_email='happyleaves.tfr@gmail.com',
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4>=4.6.3',
        'requests>=2.20.1'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ]
)
