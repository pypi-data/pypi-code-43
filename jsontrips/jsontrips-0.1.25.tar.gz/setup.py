from setuptools import setup, find_packages
from setuptools.command.install import install


with open("README.md", "r") as fh:
    long_description = fh.read()


if __name__ == "__main__":
        setup(
                name='jsontrips',
                version="0.1.25",
                author="Rik",
                author_email="rbose@cs.rochester.edu",
                description="A basic package",
                long_description=long_description,
                long_description_content_type="text/markdown",
                url="https://github.com/mrmechko/jsontrips",
                packages=find_packages(exclude=["test", "code"]),
                package_data={
                    "jsontrips": ['data/*.json']
                },
                classifiers=[
                    "Programming Language :: Python :: 3",
                    "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
                    "Operating System :: OS Independent"
                ]
        )
