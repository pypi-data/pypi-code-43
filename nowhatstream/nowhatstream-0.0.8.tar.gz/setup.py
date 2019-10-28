import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nowhatstream",
    version="0.0.8",
    author="Louis Lesueur",
    author_email="louis.l@nowhat.fr",
    description="The interface between apivideo and us",
    url="https://gitlab.com/NOWhatech/nowhat-stream.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)