import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="satang-pro-signer-x",
    version="0.0.1.dev1",
    author="Panu",
    author_email="Panu.suk@protonmail.com",
    description="An implementation of Satang Pro signing request scheme",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thebevrishot/satang-pro-signer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)