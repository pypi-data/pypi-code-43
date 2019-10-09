import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stop",
    version="0.0.12",
    author="Daniel Wendon-Blixrud",
    author_email="d@nielwb.com",
    description="Scratch to Python converter and creator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dantechguy/stop",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True
)