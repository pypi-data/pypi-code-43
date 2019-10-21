import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyRoIS",
    version="0.0.1",
    author="Eiichi Inohira",
    author_email="inohira.eiichi402@mail.kyutech.jp",
    description="Implementation of RoIS Framework in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://inohira.mns.kyutech.ac.jp/git/inohira/pyRoIS",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)