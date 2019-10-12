import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pusnowlib",
    version="0.0.8",
    author="Wonsup Yoon",
    author_email="pusnow@me.com",
    license="MIT License",
    description="My small python library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Pusnow/pusnowlib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "aiohttp",
        "beautifulsoup4",
    ],
)
