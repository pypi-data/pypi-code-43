import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="paynlsdk",
    version="1.0.1",
    author="Ing. R.J. van Dongen",
    author_email="rogier@sebsoft.nl",
    description="PayNL SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/paynl/python-sdk",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='PAYNL, SDK, Python',
    # Dependencies
    install_requires=[
        'marshmallow>=2,<3',
        'requests',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/paynl/python-sdk/issues',
        'Source': 'https://github.com/paynl/python-sdk/',
    },
)