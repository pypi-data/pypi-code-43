import setuptools

with open("README.md",'r') as fh:
	long_description = fh.read()

setuptools.setup(
 name="debug_hemin",
 version="0.0.2",
 author="hemin",
 author_email="hemin@aiotek.pro",
 description="PyPI Tutorial",
 long_description=long_description,
 long_description_content_type="text/markdown",
 url="https://github.com",
 packages=setuptools.find_packages(),
 classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)
