import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(name="ynitdb",
    version="0.0.3",
    description="A tiny non-volatile dictionary handler for python",
    url="https://thevoxel.net/projects/ynitdb",
    author="Vorap",
    author_email="vorap@thevoxel.net",
    long_description_content_type="text/markdown",
    license="GNU GPLv3",
    packages=setuptools.find_packages(),
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent"
    ]
)
