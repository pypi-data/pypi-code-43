import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="PyMemory",
    version="0.0.7",
    author="PyMario",
    author_email="rumu3f@gmail.com",
    description="Happy using PyMemory to read and write to computer memory.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PyMario/PyMemory",
    packages=setuptools.find_packages(exclude=['ctypes']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
    ],
    python_requires='>=3.6',
    package_data={
        'PyMemory': ['PyMemory.dll', 'PyMemory.py']
    }


)
