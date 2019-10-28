import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyseri",
    version="1.1.1",
    author="TaylorHere",
    author_email="taylorherelee@gmail.com",
    description="Python Serializer tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TaylorHere",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
