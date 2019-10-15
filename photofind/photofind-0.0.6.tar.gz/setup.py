from setuptools import setup, find_packages
from glob import glob
from os.path import basename, splitext

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('VERSION', 'r') as fh:
    version = fh.readline().strip()

setup(
    name="photofind",
    version=version,
    author="Matt Krueger",
    author_email="mkrueger@rstms.net",
    description="read filenames and output EXIF data from named files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://github.com/rstms/photofind",
    keywords='exif photo image',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    data_files=[('.',['VERSION'])],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",

    ],
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    install_requires=[
        'Click',
        'ExifRead',
        'geopy',
   ],
   entry_points={
       'console_scripts': [
           'photofind=photofind:cli',
        ],
   },
)
