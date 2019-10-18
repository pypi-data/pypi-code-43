import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requires = [
    'apiclient',
    'httplib2',
    'oauth2client']
setuptools.setup(
    name="pygdrive3fixed",
    version="0.6.3",
    author="Matheus Almeida / Tami",
    author_email="mat.almeida@live.com",
    description="Use Google Drive API v3 with a python interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TA40/pygdrive3",
    packages=setuptools.find_packages(),
	install_requires=requires,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    license="MIT"
)
