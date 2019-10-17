from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="constants_set",
    version="0.2",
    description="Simple constants sets for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/raphael-leger/constants-set",
    author="Raphaël Léger",
    author_email="raphael+pypi@nodixo.com",
    license="MIT",
    packages=["constants_set"],
    zip_safe=False,
)
