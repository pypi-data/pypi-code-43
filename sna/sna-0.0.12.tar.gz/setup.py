import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="sna",
    version="0.0.12",
    author="Erdem Aybek",
    author_email="eaybek@gmail.com",
    description=" ".join(["Search N Act"]),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eaybek/sna",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 1 - Planning",
    ],
    python_requires=">=3.6",
)
