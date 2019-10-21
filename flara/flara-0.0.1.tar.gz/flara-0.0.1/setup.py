import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flara",
    version="0.0.1",
    author="XMD",
    description="deep learning library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/flarahome/flara",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)