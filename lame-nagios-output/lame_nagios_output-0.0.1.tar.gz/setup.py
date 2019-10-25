import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lame_nagios_output",
    version="0.0.1",
    author="Thomas Hoogland",
    author_email="thoogland@ilionx.com",
    description="simple (and lame) script creating output for Nagios",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ThomasHoogland/LameNagiosOutput",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
