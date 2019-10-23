from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='ehelply-batcher',
    packages=find_packages(),  # this must be the same as the name above
    version='1.1.0',
    description='eHelply Batcher',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Shawn Clake',
    author_email='shawn.clake@gmail.com',
    url='https://github.com/ehelply/Batcher',
    keywords=[],
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'pytest',
        'ehelply-logger>=0.0.7',
    ],

)