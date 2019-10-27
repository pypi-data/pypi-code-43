import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="textconv",
    version="0.0.1",
    author="sanbaispeaking",
    author_email="sanbaispeaking@outlook.com",
    description="Convert a string to bytes type or str type",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sanbaispeaking/textconv",
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    python_requires='>=3.0',
)