import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="olr",
    version="0.0.3",
    author="Mathew Fok",
    author_email="mfok@stevens.edu",
    description="olr: Optimal Linear Regression",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.github.com/MatHatter",
    packages=setuptools.find_packages(),
    classifers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License",
        "Operating System :: OS Independent",
    ],
)
    
