from setuptools import setup, Extension

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="dora-isa",
    version="0.1.4",
    py_modules=['isa'],
    author="didone",
    url="http://www.compasso.com.br",
    author_email="tiago.didone@compasso.com.br",
    description="SQL Parser for Dora Project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)