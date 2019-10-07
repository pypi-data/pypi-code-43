import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="fortran-align",
    version="0.0.2",
    author="Tobias R. Henle",
    author_email="tobias@page23.de",
    description="Fortran comment alignment tool",
    entry_points={'console_scripts': ['falign = falign.__main__:run']},
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/TobiasRH/fortran-align",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
