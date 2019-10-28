"""
'jt_ops' Python Package for usefull global functions that
Joe Tilsed (https://linkedin.com/in/joetilsed) can use (AND SO CAN YOU!).
---
setup.py is the build script for setuptools.
It tells setuptools about your package (such as the name and version) as well as which code files to include.
"""

import setuptools

with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='jt_ops',
    version="0.0.1",
    author="Joe Tilsed",
    author_email="Joe@Tilsed.com",
    description="Python Package for usefull global functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://linkedin.com/in/joetilsed/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
	keywords="jt_ops python"
)


# That's all folks...
