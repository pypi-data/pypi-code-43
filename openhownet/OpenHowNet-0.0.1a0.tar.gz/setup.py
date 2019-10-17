import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="OpenHowNet",
    version="0.0.1a0",
    author="THUNLP",
    author_email="i@dozbear.com",
    description="OpenHowNet-API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thunlp/OpenHowNet-API/",
    packages=setuptools.find_packages(),
    install_requires=[
        "anytree",
        "tqdm",
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
