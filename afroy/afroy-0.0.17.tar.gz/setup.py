import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="afroy",
    version="0.0.017",
    author="Yousef Abdelkader",
    author_email="yousef.mkader@gmail.com",
    description="Simplifies some tasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    install_requires=['termcolor'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)