
from setuptools import setup, find_packages
from package.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='ttp-scripts',
    version=VERSION,
    description='Manage pipeline versions',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Brent Baumgartner',
    author_email='brent@twinthread.com',
    url='https://github.com/twinthread/ttp-scripts/',
    license='unlicensed',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'ttp': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        ttp = package.main:main
    """,
    install_requires=[
        "cement",
        "pandas",
        "tabulate",
        "colorlog",
        "requests",
        "jinja2"
    ]
)
