import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='InfoTransIO',
    version='0.0.1',
    author='Rafael Rayes',
    author_email='rafa@rayes.com.br',
    description='Transmit data using python with InfoTransIO',
    long_description='''No description yet''',
    long_description_content_type="text/markdown",
    url='https://sites.google.com/rayes.com.br/rafael-rayes/',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
