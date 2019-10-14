import setuptools

with open("README.txt", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nbapi",
    version="1.2.0.2",
    author="LazyNeko",
    author_email="nekobot.help@gmail.com",
    description="A small anime API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lazyneko1/nbapi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
