import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="compare_strings_lib",
    version="0.0.1",
    author="qalfaki",
    author_email="qusai.alfaki@gmail.com",
    description="module for comparing to strings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qalfaki/py-lib/cs_lib",
    packages=["strings"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
