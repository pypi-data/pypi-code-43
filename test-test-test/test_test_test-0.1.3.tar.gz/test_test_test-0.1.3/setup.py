import setuptools
#with open("README.md", "r") as fh:
#    long_description = fh.read()
setuptools.setup(
     name='test_test_test',  
     version='0.1.3',
     scripts=['abc'] ,
     author="Pratik Dani",
     author_email="danipratik91@gmail.com",
#     long_description=long_description,
   long_description_content_type="text/markdown",
#     url="https://github.com/javatechy/dokr",
     packages=setuptools.find_packages(),
 )