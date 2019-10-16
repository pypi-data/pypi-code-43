import setuptools

with open("README.md", "r") as long_description_file:
    long_description = long_description_file.read()

setuptools.setup(
    name="burpsuite",
    version="0.0.3",
    author="Julian Nash",
    author_email="julian.nash@venturidm.com",
    description="A small library for working with the Burp Suite API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Julian-Nash/burpsuite/releases/tag/0.0.3",
    packages=setuptools.find_packages(),
    install_requires=[
            "requests==2.22.0"
        ],
    classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
        ],
)
