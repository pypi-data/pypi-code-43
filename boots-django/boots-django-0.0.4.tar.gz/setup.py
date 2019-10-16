import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="boots-django",
    version="0.0.4",
    author="pedro",
    author_email="pedroh.mix@gmail.com",
    description="Pacote de layout baseado no vali",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MyNr/boots-django",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)