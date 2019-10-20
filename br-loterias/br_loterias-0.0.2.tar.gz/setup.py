import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="br_loterias",
    version="0.0.2",
    author="Luciano Vilas Boas Espiridião",
    author_email="lucianovilasboas@gmail.com",
    description="br loterias api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lucianovilasboas/br_loterias",
    packages=["br_loterias"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license = 'MIT',
    keywords = 'loterias brazil',    
    python_requires='>=3.0',
)
