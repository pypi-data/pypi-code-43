# vim: set ts=4 sts=4 sw=4 et ci nu ft=python:
import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="ukedown",
    version="1.0.0",
    author="Stuart Sears",
    author_email="stuart@sjsears.com",
    description="markdown extensions to simplify ukulele songsheet generation",
    long_description=long_description,
    long_description_type="text/markdown",
    url="https://github.com/lanky/ukedown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
    install_requires=[
        'markdown'
    ],
)
