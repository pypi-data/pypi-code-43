import setuptools


setuptools.setup(
    name="br_loterias",
    version="0.0.3",
    author="Luciano Vilas Boas Espiridião",
    author_email="lucianovilasboas@gmail.com",
    description="br loterias api",
    long_description="Br Loterias é uma API simples desenvolvida com finalidades educacionais. código python nessa api usa o site do UOL para coletar os dados dos sorteios das principais loterias do país.",
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

