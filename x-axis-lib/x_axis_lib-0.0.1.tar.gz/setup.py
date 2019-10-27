import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="x_axis_lib",
    version="0.0.1",
    author="qalfaki",
    author_email="qusai.alfaki@gmail.com",
    description="module for testing weheather 2 x axis are overlapping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qalfaki/py-lib/tree/master/x_axis_lib",
    packages=["x_axis"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
