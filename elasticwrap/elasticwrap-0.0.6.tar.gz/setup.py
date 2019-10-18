import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='elasticwrap',  
     version='0.0.6',
     author="Angelica Garcia",
     author_email="agalejo@amarello.com.mx",
     description="Wrapper to use mutiple versions of Elasticsearch",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     python_requires='>=3.6'
 )
