from setuptools import setup

def readmefile():
    with open("README.rst", "r") as fileText:
        return fileText.read()


setup(name="updelipack", version="1.0.0", description="delipak file is my files of first", packages=["delipack"],
      py_modules=["Tools"], long_description=readmefile(), author="ZC", author_email="598714971@qq.com", license=
      "MIT License")

