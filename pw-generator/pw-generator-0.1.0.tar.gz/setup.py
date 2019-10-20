import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("VERSION", "r") as fh:
    version = fh.read()

setuptools.setup(
    name="pw-generator",
    version=version,
    author="Petr Antonov",
    author_email="petr@antonov.space",
    description="Simple password generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pietro-a/pw-generator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
