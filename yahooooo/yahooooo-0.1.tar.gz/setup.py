import setuptools
with open("README.md","r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='yahooooo',  
     version='0.1',
     author="sid",
     author_email="sid.garg@gmail.com",
     description="yahooooo",
     long_description=long_description,
     long_description_content_type="text/markdown",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
