import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="easymultilogging",
    version="0.0.2",
    author="Praneeth Ponnekanti",
    author_email="praneeth.ponnekanti@gmail.com",
    description="A package to help multiLogging in Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    #url="",
    packages=setuptools.find_packages(),
    py_modules = ["easymultilogging"],
    package_dir = {'' : 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)