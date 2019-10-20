import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="microplink",
    version="0.0.1",
    author="Peter Wilton",
    author_email="peterrwilton@gmail.com",
    description="PLINK file processing with numba",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ammodramus/microplink",
    packages=setuptools.find_packages(),
    install_requires=['pandas', 'numpy', 'numba'],
    python_requires='>=2.7',
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ]
)
