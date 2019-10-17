import setuptools
#with open("README.md", "r") as fh:
#    long_description = fh.read()
setuptools.setup(
     name='emailspermuter',  
     version='0.1',
     scripts=['test'] ,
     author="Pratik Dani",
     author_email="danipratik91@gmail.com",
     description="A Docker and AWS utility package",
#     long_description=long_description,
   long_description_content_type="text/markdown",
#     url="https://github.com/javatechy/dokr",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3.7",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )