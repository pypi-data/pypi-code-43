import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bwi",
    version="0.0.5",
    author="BWI",
    author_email="contact@bwi-project.com",
    description="Package to add bwi methods into your project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://bwi-project.com",
    packages=setuptools.find_packages(),
    classifiers=[],
    python_requires='>=3.0',
)