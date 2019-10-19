import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='AutoPackaging',
    version='0.0.2',
    author='Rafael Rayes',
    author_email='rafa@rayes.com.br',
    description='Create your packages the easiest way, automaticaly!',
    long_description='''No''',
    long_description_content_type="text/markdown",
    url='',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
