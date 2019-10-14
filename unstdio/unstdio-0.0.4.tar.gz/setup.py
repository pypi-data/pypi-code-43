import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

long_description += "```python3\n"
with open(os.path.join("sample", "sample.py"), "r") as fh:
    long_description += fh.read()
long_description += "\n```"

setuptools.setup(
    name="unstdio",
    version="0.0.4",
    author="Erdem Aybek",
    author_email="eaybek@gmail.com",
    description=" ".join(
        ["unstdio for inplace manipulation of stdio"]
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eaybek/unstdio",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 1 - Planning",
    ],
    python_requires=">=3.6",
)
