import setuptools
import pycleanarch

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycleanarch",
    version=pycleanarch.__version__,
    author="Wallace Silva",
    author_email="contato@wallacesilva.com",
    maintainer='Wallace Silva',
    maintainer_email='contato@wallacesilva.com',
    description="A simple Python toolkit to work with Clean Architecture for Web ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wallacesilva/pycleanarch",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
    ],   
)