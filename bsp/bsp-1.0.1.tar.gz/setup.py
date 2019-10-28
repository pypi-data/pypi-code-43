import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bsp",
    version="1.0.1",
    author="Ayon Lee",
    author_email="i@hyurl.com",
    description="Basic Socket Protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hyurl/bsp-py",
    packages=[
        "bsp"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)