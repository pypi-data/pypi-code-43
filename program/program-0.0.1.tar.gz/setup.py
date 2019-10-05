import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name="program",
    version="0.0.1",
    author="Aditya Saky",
    author_email="aditya@saky.in",
    description="My first python package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adityasaky/program",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
