import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sfapi",
    version="1.0.6",
    author="nicocrm",
    author_email="nic@f1code.com",
    description="Simple API wrapper for Salesforce",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nicocrm/py-sfapi",
    packages=['sfapi'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests>=2.20.0'
    ]
)
