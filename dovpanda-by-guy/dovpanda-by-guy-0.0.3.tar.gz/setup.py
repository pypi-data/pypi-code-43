import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dovpanda-by-guy",
    version="0.0.3",
    author="Dean Langsam",
    author_email="deanla@gmail.com",
    description="Directions overlay for working with pandas in an analysis environment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/guysmoilov/dovpanda",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
