import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="schupy",
    version="1.0.9",
    author="Gergely Dálya, Tamás Bozóki, Kornél Kapás, János Takátsy, Ernő Prácser, Gabriella Sátori",
    author_email="dalyag@caesar.elte.hu",
    description="A python package for modeling Schumann resonances",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dalyagergely/schupy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
