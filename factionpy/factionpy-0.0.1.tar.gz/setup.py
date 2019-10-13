import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="factionpy",
    version="0.0.1",
    author="The Faction Team",
    author_email="team@factionc2.com",
    description="Common Library for Python based Faction services.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FactionC2/factionpy",
    packages=setuptools.find_packages(),
    classifiers=[],
    python_requires='>=3.6',
)