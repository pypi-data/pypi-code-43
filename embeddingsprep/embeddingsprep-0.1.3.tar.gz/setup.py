import setuptools

with open("../embeddings/README.md", "r") as fh:
    long_description = fh.read()

with open("../embeddings/requirements.txt", "r") as fh:
    req = fh.read().split("\n")

setuptools.setup(
    name="embeddingsprep",
    version="0.1.3",
    author="sally14",
    author_email="sally14.doe@gmail.com",
    description="A word2vec preprocessing and training package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sally14/embeddings",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=req,
)
