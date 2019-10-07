import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='pydatacleaner',
     version='0.1.2.5',
     author="Kevin Crouse",
     author_email="krcrouse@gmail.com",
     description="A small utility designed to process/parse/clean scalars, especially text. (note: in active development)",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://gitlab.com/krcrouse/datacleaner",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3.7",
         "License :: OSI Approved :: Apache Software License",
         "Operating System :: OS Independent",
         "Development Status :: 3 - Alpha"
     ],
 )
