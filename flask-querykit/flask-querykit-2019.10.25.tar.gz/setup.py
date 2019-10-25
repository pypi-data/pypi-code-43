import setuptools

long_description = "A useful kit makes flask's query more pythonic."

setuptools.setup(
	name = "flask-querykit",
	version="2019.10.25",
	auth="derick",
	author_email="13750192465@163.com",
	description=long_description,
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/suckmybigdick/flask-querykit",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	install_requires=[
		"Flask==1.0.2",
		"mongoengine==0.18.0",
		"flask_mongoengine==0.9.5",
		"setuptools==41.0.1",
	],
)




