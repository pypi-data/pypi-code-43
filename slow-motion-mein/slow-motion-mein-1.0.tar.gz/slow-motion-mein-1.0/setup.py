import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='slow-motion-mein',  
     version='1.0',
     scripts=['slow-motion-mein'] ,
     author="Wacky Bot",
     author_email="IItkabaapiet@gmail.com",
     description="And AWS plus some script cool utility package",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/shinhacker/slow-motion-mein",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
