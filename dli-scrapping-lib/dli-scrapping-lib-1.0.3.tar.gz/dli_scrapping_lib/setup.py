import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dli-scrapping-lib",
    version="1.0.0",
    author="David Li",
    author_email="davidli012345@gmail.com",
    description="Open Source Library of all the scrapping python utilities I have used over the years",
    long_description=long_description,
    long_description_content_type="text/rst",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)