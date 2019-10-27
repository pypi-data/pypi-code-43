import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sequence_builder",
    version="0.0.2",
    author="DoraSz",
    author_email="szuucs.dora@gmail.com",
    description="Building sequences from time-series data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DoraSz/sequenceBuilder",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
	install_requires=[
          'numpy',
          'pandas'
      ]
)