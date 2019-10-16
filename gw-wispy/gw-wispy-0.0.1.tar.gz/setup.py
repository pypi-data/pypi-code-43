import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gw-wispy",
    version="0.0.1",
    author="Sebastian Khan",
    author_email="KhanS22@Cardiff.ac.uk",
    description="A package to work with gravitational waveforms from compact binary systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/SpaceTimeKhantinuum/wispy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.7',
)
