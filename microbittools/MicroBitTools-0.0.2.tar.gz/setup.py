from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="MicroBitTools",
    version="0.0.2",
    description="Library used for helping developing for the BBC microbit easier.",
    py_modules=["MicroBitTools"],
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: Microsoft :: Windows :: Windows 10",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BigCowKing/MicroBitTools",
    author="Simon Lindgren",
    author_email="babbilant@outlook.com",
)