import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PhilippeCantrelle2ADatavizTest3",
    version="0.0.1",
    author="Philippe Cantrelle",
    author_email="philippe.cantrelle@ensae.fr",
    description="Package dataviz 2A ensae Philippe Cantrelle",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)