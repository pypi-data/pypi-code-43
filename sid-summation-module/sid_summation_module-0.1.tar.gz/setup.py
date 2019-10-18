import setuptools
with open("README.md","r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='sid_summation_module',  
     version='0.1',
     author="siddharth garg",
     author_email="sidd.garg786@gmail.com",
     description="module for summation of two numbers",
     long_description=long_description,
     long_description_content_type="text/markdown",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
