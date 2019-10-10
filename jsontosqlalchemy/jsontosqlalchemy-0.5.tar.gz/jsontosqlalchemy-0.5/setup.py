import setuptools

with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(

     name='jsontosqlalchemy',  

     version='0.5',

     scripts=[] ,

     author="Carlos Rodriguez",

     author_email="diablocharly@hotmail.com",

     description="Extract any Json to models sqlalchemy",

     long_description=long_description,

   long_description_content_type="text/markdown",

     url="https://github.com/CarlosRCDev/jsontosqlalchemy",

     download_url = 'https://github.com/CarlosRCDev/jsontosqlalchemy/archive/0.5.tar.gz',

     install_requires=[
          'numpy',
      ],

    #  packages=setuptools.find_packages(),

     classifiers=[

         "Programming Language :: Python :: 3",

         "License :: OSI Approved :: MIT License",

         "Operating System :: OS Independent",

     ],

 )