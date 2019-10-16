import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rouge_score",
    version="0.0.2",
    author="Peter J. Liu",
    author_email="peterjliu@gmail.com",
    description="Pure python implementation of ROUGE-1.5.5.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/google-research/google-research/tree/master/rouge",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
