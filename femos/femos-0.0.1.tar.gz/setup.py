import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="femos",
    version="0.0.1",
    author="estissy",
    author_email="estissy@gmail.com",
    description="My small library for neuroevolution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/estissy/femos",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requirements=">=3.0",
)
