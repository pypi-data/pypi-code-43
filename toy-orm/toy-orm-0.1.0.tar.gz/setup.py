import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="toy-orm",
    version="0.1.0",
    author="Juliano Silva",
    author_email="julianosoaresdasilva@outlook.com",
    description="A small ORM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/julianossilva/toy-orm",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)