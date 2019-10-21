import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="multilines-Piturnah",
    version="0.0.8",
    author="Piturnah",
    author_email="peterhebden6@gmail.com",
    description="Beautification tools for text based devs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Piturnah/multilines",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
