
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="algebraic-data-type",
    version="0.0.4",
    author="Caleb Foong",
    author_email="catethos@gmail.com",
    description="Algebraic data type and pattern matching",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/catethos/adt",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "pampy"
    ],
    license='The MIT License'

)

