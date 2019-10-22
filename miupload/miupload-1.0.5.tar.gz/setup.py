import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="miupload",
    version="1.0.5",
    author="Juraj Vasek",
    author_email="juraj.vasek@minerva.kgi.edu",
    description="Small lighweight library for collecting and distribution of jupyter notebooks during SSS on MSaKGI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)