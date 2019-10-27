import os
from setuptools import setup






setup(
    name = "Giraffe2D",
    version = '1.1.17',
    description = "This Is A PyGame Powered And OpenGL Powered Game Engine", 
    install_requires=["wget", "pygame", "PyOpenGL", "pytmx"],
    py_modules=["Giraffe2D"],
    package_dir = {'': 'Engine'},
    url='https://github.com/CrypticCoding/Girrafee2D',
    author="Saugat Siddiky Jarif",
    author_email="saugatjarif@gmail.com",
    license="MIT",
    long_description="A Distribution By Saugat Siddiky Jarif",
    
)
