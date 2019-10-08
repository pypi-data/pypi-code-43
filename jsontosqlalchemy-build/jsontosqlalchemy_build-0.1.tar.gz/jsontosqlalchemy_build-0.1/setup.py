import setuptools

with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(

     name='jsontosqlalchemy_build',  

     version='0.1',

     scripts=['jsontosqlalchemy'] ,

     author="Carlos Rodriguez",

     author_email="diablocharly@hotmail.com",

     description="Extract any Json to models sqlalchemy",

     long_description=long_description,

   long_description_content_type="text/markdown",

     url="https://github.com/CarlosRCDev/jsontosqlalchemy",

     packages=setuptools.find_packages(),

     classifiers=[

         "Programming Language :: Python :: 3",

         "License :: OSI Approved :: MIT License",

         "Operating System :: OS Independent",

     ],

 )