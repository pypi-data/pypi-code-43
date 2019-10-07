import setuptools
with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name='salesforce-dbsync',
	version='1.3.3',
	author="S Satapathy",
	author_email="shubhakant.satapathy@gmail.com",
	description="Python library to download data from Salesforce and synchronize with a relational database",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/satapathy/pypi-salesforce-dbsync",
	packages=setuptools.find_packages(),
	install_requires=[
		'simple_salesforce',
		'mysql.connector',
		'screenwriter',
	],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
 )
