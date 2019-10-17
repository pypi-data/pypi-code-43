import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pychronicles",
    version="0.0.5",
    author="Thomas Guyet",
    author_email="thomas.guyet@irisa.fr",
    description="A package for chronicle recognition",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.inria.fr/tguyet/pychronicles",
    install_requires=['numpy','scipy','lazr.restfulclient','lazr.uri','lark-parser'],
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
