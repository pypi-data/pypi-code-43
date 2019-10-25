import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='RuNAs',  
     version='0.0.1',
     scripts=['runas'] ,
     author="Roberto Villegas-Diaz",
     author_email="villegas.roberto@hotmail.com",
     description="RNAseq pipeline",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/villegar/runas/tree/v2",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     python_requires = '>=3.6',
)

