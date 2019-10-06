import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="currencyexchanger",
    version="1.0.0",
    author="Suraj Karki",
    author_email="suraj.karki500@gmail.com",
    description="This is a simple python package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/surajkarki66/python-module",
    #packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    packages=["currency_exchanger"],
    include_package_data=True,
    install_requires = ["requests","cachetools"]


   

)
