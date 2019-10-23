import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyannotations",
    version="0.0.3",
    author="Pavel V. Pristupa",
    author_email="pristupa@gmail.com",
    description="Annotating Python classes with decorators",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pristupa/pyannotations",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
