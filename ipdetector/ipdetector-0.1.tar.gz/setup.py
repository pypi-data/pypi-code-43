from setuptools import setup

with open("README.md","r") as f:
    long_description = f.read()

setup(
    name='ipdetector',
    version='0.1',
    description='Detect whether the given input is Public IP/ Private IP/ Public IP range or Private IP range',
    py_modules=["ipdetector"],
    package_dir={'':'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/1uffyD9/ipdetector",
    author="1uffyD9",
    author_email="mugiwara.luffyd9@gmail.com",

)
