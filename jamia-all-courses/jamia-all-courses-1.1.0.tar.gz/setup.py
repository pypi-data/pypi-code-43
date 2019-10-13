import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / 'README.md').read_text()

# This call to setup() does all the work
setup(
    name='jamia-all-courses',
    version='1.1.0',
    description='A helpers for getting all courses available in Jamia Millia Islamia.',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/Faisal-Manzer/jamia-all-courses',
    author='Faisal Manzer',
    author_email='faisal_manzer@yahoo.in',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=['jamia_all_courses'],
    include_package_data=True,
    download_url='https://github.com/Faisal-Manzer/jamia-all-courses/archive/Python.tar.gz',
    entry_points={
    },
)
