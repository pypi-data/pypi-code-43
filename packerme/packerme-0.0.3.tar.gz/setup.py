import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="packerme",####the same name as the name in the __init__.py
    version="0.0.3",
    author="Yousef Abdelkader",
    author_email="yousef.mkader@gmail.com",
    description="Simplifies Creating And Publishing Pypi Packages",
    long_description=long_description,####Change Everything except this and the line under
    long_description_content_type="text/markdown",
    url="",
    install_requires=[],###non default modules that you import in your code seperated by comas and in between ""
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)