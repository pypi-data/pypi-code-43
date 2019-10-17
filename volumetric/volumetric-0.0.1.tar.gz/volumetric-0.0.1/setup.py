import setuptools

setuptools.setup(
    name="volumetric",
    version="0.0.1",
    author="volatilityfoundation",
    author_email="author@example.com",
    description="A small example package",
    long_description="dummy package",
    url="https://github.com/volatilityfoundation/volumetric",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5.3',
)