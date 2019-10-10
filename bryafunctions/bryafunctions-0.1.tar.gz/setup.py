from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
     name='bryafunctions',  
     version='0.1',
     author="Zac Bryant",
     author_email="zac.bryant15@gmail.com",
     description="Python Functions in relation to BryaSoftware Tutorials, learn more at my GitHub or www.bryasoftware.com",
     url="https://github.com/BryaSoftware/BryaFunctions",
     packages=['bryafunctions'],
     long_description=long_description,
     long_description_content_type="text/markdown",
     zip_safe=False
 )
 