import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

exec(open('bpsgeodb/version.py').read())

setuptools.setup(
    name="bpsgeodb",
    version=__version__,
    author="Brazil Petrostudies Servicos Geologicos Ltda",
    author_email="support@brazilpetrostudies.com.br",
    description="BPS Geodatabase - API Authorization and Access Python Modules",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brazil-petrostudies/python-bpsgeodb",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
