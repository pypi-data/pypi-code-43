import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="command-known-as-dan",
	version="1.0.1",
	author="known-as-dan",
	author_email="dan@gotoindex.com",
	description="Command is a simple framework for handling command execution within your python application.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/known-as-dan/command-pypi",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent"
	],
	python_requires=">=3.6"
)