import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rbxthon",
    version="0.1.1",
    author="Gordxn",
    author_email="",
    description="Open-Source Roblox API built with Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gordxn/Rbxthon",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)