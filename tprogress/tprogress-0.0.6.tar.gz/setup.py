import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tprogress",
    version="0.0.6",
    author="Thorsten Hapke",
    author_email="thorsten.hapke@sap.com",
    description="time monitoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thhapke/tprogress",
    keywords = ['time keeping', 'time monitoring'],
    packages=setuptools.find_packages(),
    classifiers=[
    	'Programming Language :: Python :: 3.5',
    	'Programming Language :: Python :: 3.6',
    	'Programming Language :: Python :: 3.7',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)