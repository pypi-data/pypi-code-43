import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vterminal",
    version="1.1.0",
    author="Vincent Glendenning",
    author_email="vincentglendenning@gmail.com",
    description="A terminal emulator using pygame.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mutater/vterminal",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)